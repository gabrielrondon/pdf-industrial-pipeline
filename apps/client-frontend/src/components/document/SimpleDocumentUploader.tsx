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

  // Smooth progress animation - flui até 100%
  useEffect(() => {
    if (!isUploading) return;
    
    const smoothProgressUpdate = () => {
      setDisplayProgress(prev => {
        if (prev < progress) {
          // Incremento mais suave e consistente
          const increment = Math.min(Math.random() * 1.5 + 0.3, progress - prev);
          return Math.min(prev + increment, progress);
        }
        return prev;
      });
    };

    const progressInterval = setInterval(smoothProgressUpdate, 150);
    return () => clearInterval(progressInterval);
  }, [progress, isUploading]);

  // Progress simulation for better UX - garante que chegue a 100%
  useEffect(() => {
    if (!isUploading) return;
    
    const simulateProgress = () => {
      setProgress(prev => {
        if (prev < 85) {
          // Progresso mais rápido até 85%
          const timeIncrement = Math.random() * 0.8 + 0.2;
          return Math.min(prev + timeIncrement, 85);
        } else if (prev < 95) {
          // Progresso mais lento entre 85-95% para parecer mais realístico
          const timeIncrement = Math.random() * 0.3 + 0.1;
          return Math.min(prev + timeIncrement, 95);
        }
        return prev;
      });
    };

    const simulationInterval = setInterval(simulateProgress, 400);
    return () => clearInterval(simulationInterval);
  }, [isUploading]);

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

    const maxSize = parseInt(import.meta.env.VITE_MAX_FILE_SIZE || '209715200'); // 200MB default
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
              const processingProgress = status.progress || 70;
              setProgress(Math.min(processingProgress, 95)); // Máximo 95% durante processing
              break;
            case 'completed':
              setProgress(100); // Só vai para 100% quando realmente completed
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
    <div className="w-full">
      {/* Premium Upload Card */}
      <div className="bg-gradient-to-r from-arremate-navy-600 to-arremate-navy-700 p-12 rounded-xl border border-arremate-navy-800 shadow-lg mb-6">
        <div className="text-center mb-8">
          <div className="bg-arremate-gold-500 p-4 rounded-full w-fit mx-auto mb-6">
            <svg className="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Análise Inteligente de Documentos
          </h1>
          <p className="text-xl text-arremate-navy-200 max-w-3xl mx-auto leading-relaxed">
            Faça upload de editais de leilão e processos judiciais para identificação automática de oportunidades
          </p>
        </div>

        {/* Premium File Input */}
        <div className="bg-white p-6 rounded-lg border-2 border-dashed border-arremate-navy-300 hover:border-arremate-gold-500 transition-all">
          <div className="space-y-4">
            <Input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={isUploading}
              className="cursor-pointer border-arremate-navy-200 focus:border-arremate-gold-500 focus:ring-arremate-gold-500"
            />
            {file && (
              <div className="flex items-center gap-3 p-3 bg-arremate-navy-50 rounded-lg border border-arremate-navy-200">
                <FileText className="h-5 w-5 text-arremate-navy-600" />
                <div className="flex-1">
                  <div className="font-semibold text-arremate-navy-900">{file.name}</div>
                  <div className="text-sm text-arremate-navy-600">({Math.round(file.size / (1024 * 1024))}MB)</div>
                </div>
              </div>
            )}
            
            {/* Botão de Upload dentro do quadro azul */}
            <div className="flex gap-4 pt-2">
              <Button
                onClick={handleUpload}
                disabled={!file || isUploading || !user}
                size="lg"
                className="flex-1 bg-arremate-gold-500 hover:bg-arremate-gold-600 text-arremate-gold-900 font-semibold py-3 shadow-lg"
              >
                {isUploading ? (
                  <>
                    <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                    Processando...
                  </>
                ) : (
                  <>
                    <Upload className="h-5 w-5 mr-2" />
                    Fazer Upload
                  </>
                )}
              </Button>

              {(file || error) && (
                <Button 
                  variant="outline" 
                  onClick={handleReset} 
                  disabled={isUploading}
                  size="lg"
                  className="border-arremate-charcoal-300 text-arremate-charcoal-700 hover:bg-arremate-charcoal-50"
                >
                  <X className="h-4 w-4 mr-2" />
                  Limpar
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Progress Card */}
      {isUploading && (
        <div className="bg-white p-6 rounded-xl border border-arremate-charcoal-200 shadow-sm mb-6">
          <div className="space-y-4">
            {/* Enhanced Progress Bar */}
            <div className="space-y-3">
              <div className="w-full bg-arremate-navy-100 rounded-full h-4 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-arremate-gold-500 to-arremate-gold-600 rounded-full transition-all duration-500 ease-out relative"
                  style={{ width: `${displayProgress}%` }}
                >
                  <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-arremate-gold-500 rounded-full animate-pulse"></div>
                  <span className="text-arremate-navy-700 font-medium">
                    {getStatusMessage()}
                  </span>
                </div>
                <span className="font-mono text-lg font-bold text-arremate-gold-700">
                  {Math.floor(displayProgress)}%
                </span>
              </div>
            </div>
            
            {/* Processing Tip */}
            <div className="bg-arremate-gold-50 p-4 rounded-lg border border-arremate-gold-200">
              <div className="flex items-center gap-2 text-sm text-arremate-gold-800">
                <span className="text-lg">💡</span>
                <span className="font-medium">
                  Dica: Enquanto isso, que tal preparar seus documentos para o próximo leilão?
                </span>
              </div>
            </div>
            
            {currentJobId && (
              <div className="text-xs text-center text-arremate-charcoal-500 font-mono bg-arremate-charcoal-50 p-2 rounded">
                Job ID: {currentJobId}
              </div>
            )}
          </div>
        </div>
      )}


      {/* Error Card */}
      {error && (
        <div className="bg-red-50 p-6 rounded-xl border border-red-200 shadow-sm mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-red-100 p-2 rounded-lg">
              <AlertCircle className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <h3 className="font-semibold text-red-900">Erro no Upload</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Success Card */}
      {jobStatus?.status === 'completed' && (
        <div className="bg-green-50 p-6 rounded-xl border border-green-200 shadow-sm mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-green-900">Sucesso!</h3>
              <p className="text-green-700">Documento processado com sucesso.</p>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}