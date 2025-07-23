/**
 * SimpleDocumentUploader - Versão simplificada que usa nossa API Railway
 * Em vez de Supabase diretamente (que causa problemas de RLS)
 */

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, FileText, AlertCircle, CheckCircle, X, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/components/ui/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '@/contexts/DocumentContext';
import { railwayApi, JobStatus } from '@/services/railwayApiService';
import { transformRailwayResultsToDocumentAnalysis } from '@/utils/dataTransformers';

interface SimpleDocumentUploaderProps {
  onAnalysisComplete?: (results: any) => void;
}

// Mensagens divertidas estilo Discord para aliviar a ansiedade do usuário
const funnyMessages = [
  'Arremate360 está trabalhando... 🔍',
  'Mais um pouco, ok? ⏰',
  'Analisando cada vírgula... 📋',
  'Procurando as melhores oportunidades... 💎',
  'Quase terminando... prometo! 🤞',
  'Descobrindo tesouros escondidos... 🏆',
  'Verificando se vale a pena... 💰',
  'Mais alguns segundos... ☕',
  'Garimpando informações valiosas... ⛏️',
  'Paciência, estamos quase lá! 🚀',
  'Processando com amor e carinho... ❤️',
  'Conectando os pontos... 🔗',
  'Fazendo a mágica acontecer... ✨',
  'Checando os detalhes importantes... 🔎',
  'Quase pronto para te surpreender! 🎉'
];

let messageIndex = 0;

export function SimpleDocumentUploader({ onAnalysisComplete }: SimpleDocumentUploaderProps) {
  const { user } = useAuth();
  const { addDocument, refreshDocuments } = useDocuments();
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [displayProgress, setDisplayProgress] = useState(0);
  const [currentMessage, setCurrentMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Smooth progress animation
  useEffect(() => {
    if (!isUploading) return;
    
    const smoothProgressUpdate = () => {
      setDisplayProgress(prev => {
        if (prev < progress) {
          // Incrementally increase by 1-2% every 200ms
          const increment = Math.min(Math.random() * 2 + 0.5, progress - prev);
          return Math.min(prev + increment, progress);
        }
        return prev;
      });
    };

    const progressInterval = setInterval(smoothProgressUpdate, 200);
    return () => clearInterval(progressInterval);
  }, [progress, isUploading]);

  // Update message every 2-3 seconds
  useEffect(() => {
    if (!isUploading) return;
    
    const updateMessage = () => {
      const message = funnyMessages[messageIndex % funnyMessages.length];
      messageIndex++;
      setCurrentMessage(message);
    };

    updateMessage(); // Initial message
    const messageInterval = setInterval(updateMessage, 2500);
    return () => clearInterval(messageInterval);
  }, [isUploading]);

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
    setDisplayProgress(0);
    setCurrentMessage('');

    try {
      toast({
        title: "Iniciando upload",
        description: `Enviando ${file.name}...`,
      });

      // Upload do arquivo para nossa API Railway
      const uploadResult = await railwayApi.uploadDocument(file, user.id);
      
      if (!uploadResult.success) {
        throw new Error(uploadResult.error || 'Erro no upload');
      }

      setProgress(50);
      setCurrentJobId(uploadResult.job_id || null);

      toast({
        title: "Upload realizado!",
        description: "Processamento iniciado. Aguarde os resultados...",
      });

      // Create document entry for immediate navigation
      const documentAnalysis = {
        id: uploadResult.job_id || `upload-${Date.now()}`,
        userId: user?.id || '',
        fileName: file?.name || 'documento.pdf',
        fileUrl: '',
        type: 'edital' as const,
        uploadedAt: new Date().toISOString(),
        analyzedAt: new Date().toISOString(),
        isPrivate: false,
        points: []
      };

      // Save document to context so it appears in "Meus Documentos"
      try {
        console.log('📝 Salvando documento no contexto...', documentAnalysis.id);
        addDocument(documentAnalysis);
        console.log('✅ Documento salvo na lista "Meus Documentos"');
      } catch (error) {
        console.error('❌ Erro ao salvar documento:', error);
      }

      // Se temos um job_id, monitorar o progresso
      if (uploadResult.job_id) {
        setCurrentJobId(uploadResult.job_id);
        // Start monitoring and wait for completion before redirecting
        await monitorJob(uploadResult.job_id);
        
        console.log('🚀 Redirecionando para página de análise...');
        navigate(`/documents/${documentAnalysis.id}`);
      } else {
        // Upload simples sem job tracking
        setProgress(100);
        toast({
          title: "Upload concluído!",
          description: "Redirecionando para análise...",
        });
        
        setTimeout(() => {
          console.log('🚀 Redirecionando para página de análise...');
          navigate(`/documents/${documentAnalysis.id}`);
        }, 2000);
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

  const monitorJob = async (jobId: string): Promise<void> => {
    return new Promise((resolve, reject) => {
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
                title: "Análise concluída!",
                description: "Processamento finalizado com sucesso.",
              });
              // Refresh documents to get the analysis results
              console.log('🔄 Análise concluída, atualizando lista de documentos...');
              try {
                await refreshDocuments();
                console.log('✅ Lista de documentos atualizada com resultados da análise!');
                resolve(); // Resolve the promise when completed
              } catch (error) {
                console.error('❌ Erro ao atualizar documentos:', error);
                resolve(); // Still resolve even if refresh fails
              }
              return; // Para o loop
            case 'failed':
              reject(new Error(status.error || 'Processamento falhou'));
              return;
          }

          // Continuar monitorando se não terminou
          attempts++;
          if (attempts < maxAttempts) {
            setTimeout(checkStatus, 5000); // Check a cada 5 segundos
          } else {
            reject(new Error('Timeout: processamento demorou mais que o esperado'));
          }

        } catch (error: any) {
          console.error('Erro ao verificar status:', error);
          setError(`Erro no processamento: ${error.message}`);
          reject(error);
        }
      };

      checkStatus();
    });
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
    if (!jobStatus) {
      return isUploading && currentMessage ? currentMessage : null;
    }
    
    switch (jobStatus.status) {
      case 'pending':
        return currentMessage || 'Aguardando processamento...';
      case 'processing':
        return currentMessage || 'Processando documento...';
      case 'completed':
        return 'Documento processado com sucesso! 🎯';
      case 'failed':
        return 'Ops! Algo deu errado... 😅';
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
            <Progress value={displayProgress} className="w-full h-3 transition-all duration-300 ease-out" />
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-blue-600 font-medium animate-pulse">
                  {getStatusMessage()}
                </span>
                <span className="font-mono text-blue-700">
                  {Math.floor(displayProgress)}%
                </span>
              </div>
              {isUploading && (
                <div className="text-xs text-gray-500 text-center">
                  💡 Dica: Enquanto isso, que tal preparar seus documentos para o próximo leilão?
                </div>
              )}
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