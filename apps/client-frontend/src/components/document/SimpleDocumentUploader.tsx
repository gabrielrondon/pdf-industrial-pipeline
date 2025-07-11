/**
 * SimpleDocumentUploader - Versão simplificada que usa nossa API Railway
 * Em vez de Supabase diretamente (que causa problemas de RLS)
 */

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, FileText, AlertCircle, CheckCircle, X, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/components/ui/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { railwayApi, JobStatus } from '@/services/railwayApiService';
import { transformRailwayResultsToDocumentAnalysis } from '@/utils/dataTransformers';

interface SimpleDocumentUploaderProps {
  onAnalysisComplete?: (results: any) => void;
}

export function SimpleDocumentUploader({ onAnalysisComplete }: SimpleDocumentUploaderProps) {
  const { user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Verificar se o arquivo é válido
  const validateFile = (file: File): string | null => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return 'Apenas arquivos PDF são permitidos';
    }

    const maxSize = parseInt(import.meta.env.VITE_MAX_FILE_SIZE || '104857600'); // 100MB default
    if (file.size > maxSize) {
      const maxSizeMB = Math.round(maxSize / (1024 * 1024));
      return `Arquivo muito grande. Máximo permitido: ${maxSizeMB}MB`;
    }

    return null;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    const validationError = validateFile(selectedFile);
    if (validationError) {
      setError(validationError);
      return;
    }

    setFile(selectedFile);
    setError(null);
    setProgress(0);
    setJobStatus(null);
    setCurrentJobId(null);
  };

  const handleUpload = async () => {
    if (!file || !user) return;

    setIsUploading(true);
    setError(null);
    setProgress(10);

    try {
      toast({
        title: "Iniciando upload",
        description: `Enviando ${file.name}...`,
      });

      // Upload do arquivo para nossa API Railway
      const uploadResult = await railwayApi.uploadDocument(file);
      
      if (!uploadResult.success) {
        throw new Error(uploadResult.error || 'Erro no upload');
      }

      setProgress(50);
      setCurrentJobId(uploadResult.job_id || null);

      toast({
        title: "Upload realizado!",
        description: "Processamento iniciado. Aguarde os resultados...",
      });

      // Se temos um job_id, monitorar o progresso
      if (uploadResult.job_id) {
        await monitorJob(uploadResult.job_id);
      } else {
        // Upload simples sem job tracking
        setProgress(100);
        toast({
          title: "Sucesso!",
          description: "Arquivo processado com sucesso.",
        });
      }

    } catch (error: any) {
      console.error('Erro no upload:', error);
      setError(`Erro ao fazer upload: ${error.message}`);
      toast({
        title: "Erro no upload",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const monitorJob = async (jobId: string) => {
    let attempts = 0;
    const maxAttempts = 60; // 5 minutos máximo (5s intervalo)

    const checkStatus = async () => {
      try {
        const status = await railwayApi.getJobStatus(jobId);
        setJobStatus(status);

        switch (status.status) {
          case 'pending':
            setProgress(30);
            break;
          case 'processing':
            setProgress(status.progress || 70);
            break;
          case 'completed':
            setProgress(100);
            toast({
              title: "Processamento concluído!",
              description: "Análise do documento finalizada.",
            });
            if (onAnalysisComplete && status.results) {
              // Transform Railway API results to DocumentAnalysis format
              const documentAnalysis = transformRailwayResultsToDocumentAnalysis(
                status.results,
                jobId,
                file?.name || 'documento.pdf'
              );
              onAnalysisComplete(documentAnalysis);
            }
            return; // Para o loop
          case 'failed':
            throw new Error(status.error || 'Processamento falhou');
        }

        // Continuar monitorando se não terminou
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(checkStatus, 5000); // Check a cada 5 segundos
        } else {
          throw new Error('Timeout: processamento demorou mais que o esperado');
        }

      } catch (error: any) {
        console.error('Erro ao verificar status:', error);
        setError(`Erro no processamento: ${error.message}`);
      }
    };

    checkStatus();
  };

  const handleReset = () => {
    setFile(null);
    setProgress(0);
    setError(null);
    setIsUploading(false);
    setCurrentJobId(null);
    setJobStatus(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStatusMessage = () => {
    if (!jobStatus) return null;
    
    switch (jobStatus.status) {
      case 'pending':
        return 'Aguardando processamento...';
      case 'processing':
        return 'Processando documento...';
      case 'completed':
        return 'Processamento concluído!';
      case 'failed':
        return 'Erro no processamento';
      default:
        return 'Status desconhecido';
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Upload de Documento PDF
        </CardTitle>
        <CardDescription>
          Envie um arquivo PDF para análise usando nossa API
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* File Input */}
        <div className="space-y-2">
          <Input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            disabled={isUploading}
            className="cursor-pointer"
          />
          {file && (
            <div className="text-sm text-muted-foreground">
              Arquivo selecionado: {file.name} ({Math.round(file.size / (1024 * 1024))}MB)
            </div>
          )}
        </div>

        {/* Progress */}
        {isUploading && (
          <div className="space-y-2">
            <Progress value={progress} className="w-full" />
            <div className="text-sm text-center text-muted-foreground">
              {getStatusMessage() || `${progress}% concluído`}
            </div>
            {currentJobId && (
              <div className="text-xs text-center text-muted-foreground">
                Job ID: {currentJobId}
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erro</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Success */}
        {jobStatus?.status === 'completed' && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertTitle>Sucesso!</AlertTitle>
            <AlertDescription>
              Documento processado com sucesso.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>

      <CardFooter className="flex gap-2">
        <Button
          onClick={handleUpload}
          disabled={!file || isUploading || !user}
          className="flex-1"
        >
          {isUploading ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Processando...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4 mr-2" />
              Fazer Upload
            </>
          )}
        </Button>

        {(file || error) && (
          <Button variant="outline" onClick={handleReset} disabled={isUploading}>
            <X className="h-4 w-4 mr-2" />
            Limpar
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}