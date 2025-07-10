import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  RefreshCw,
  Play,
  Square,
  BarChart3
} from 'lucide-react';
import LargeDocumentService, { ProcessingJob, ProcessingConfig } from '@/services/largeDocumentService';
import { useToast } from '@/hooks/use-toast';

interface LargeDocumentProcessorProps {
  documentId: string;
  fileUrl: string;
  fileName: string;
  fileSize: number;
  model?: string;
  documentType?: string;
  config?: ProcessingConfig;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

const LargeDocumentProcessor: React.FC<LargeDocumentProcessorProps> = ({
  documentId,
  fileUrl,
  fileName,
  fileSize,
  model = 'native',
  documentType = 'edital',
  config,
  onComplete,
  onError
}) => {
  const [processingJob, setProcessingJob] = useState<ProcessingJob | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [cleanupMonitor, setCleanupMonitor] = useState<(() => void) | null>(null);
  const { toast } = useToast();

  const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(2);
  const shouldUseLargeProcessing = LargeDocumentService.shouldUseLargeProcessing(fileSize);

  // Load initial processing status
  useEffect(() => {
    loadProcessingStatus();
    loadStats();
  }, [documentId]);

  // Cleanup monitor on unmount
  useEffect(() => {
    return () => {
      if (cleanupMonitor) {
        cleanupMonitor();
      }
    };
  }, [cleanupMonitor]);

  const loadProcessingStatus = useCallback(async () => {
    try {
      const status = await LargeDocumentService.getProcessingStatus(documentId);
      setProcessingJob(status);
      
      if (status && (status.status === 'processing' || status.status === 'pending')) {
        setIsProcessing(true);
        startMonitoring();
      }
    } catch (error) {
      console.error('Failed to load processing status:', error);
    }
  }, [documentId]);

  const loadStats = useCallback(async () => {
    try {
      const statistics = await LargeDocumentService.getProcessingStats(documentId);
      setStats(statistics);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }, [documentId]);

  const startMonitoring = useCallback(() => {
    if (cleanupMonitor) return; // Already monitoring

    const cleanup = LargeDocumentService.monitorProcessing(
      documentId,
      (job) => {
        setProcessingJob(job);
      },
      (result) => {
        setProcessingJob(result);
        setIsProcessing(false);
        loadStats();
        toast({
          title: "Processamento Concluído",
          description: `Documento processado com sucesso!`,
        });
        if (onComplete) onComplete(result);
      },
      (error) => {
        setIsProcessing(false);
        toast({
          title: "Erro no Processamento",
          description: error,
          variant: "destructive",
        });
        if (onError) onError(error);
      }
    );

    cleanup.then(setCleanupMonitor);
  }, [documentId, cleanupMonitor, onComplete, onError, toast, loadStats]);

  const handleStartProcessing = async () => {
    try {
      setIsProcessing(true);
      
      const result = await LargeDocumentService.startProcessing(
        documentId,
        fileUrl,
        model,
        documentType,
        config
      );

      if (result.success) {
        toast({
          title: "Processamento Iniciado",
          description: `Processamento de documento grande iniciado para ${fileName}`,
        });
        startMonitoring();
      }
    } catch (error) {
      setIsProcessing(false);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      toast({
        title: "Erro ao Iniciar",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const handleCancelProcessing = async () => {
    try {
      const success = await LargeDocumentService.cancelProcessing(documentId);
      if (success) {
        setIsProcessing(false);
        if (cleanupMonitor) {
          cleanupMonitor();
          setCleanupMonitor(null);
        }
        toast({
          title: "Processamento Cancelado",
          description: "O processamento foi cancelado com sucesso.",
        });
      }
    } catch (error) {
      toast({
        title: "Erro ao Cancelar",
        description: "Não foi possível cancelar o processamento.",
        variant: "destructive",
      });
    }
  };

  const handleRetryProcessing = async () => {
    try {
      setIsProcessing(true);
      
      const result = await LargeDocumentService.retryProcessing(
        documentId,
        fileUrl,
        model,
        documentType,
        config
      );

      if (result.success) {
        toast({
          title: "Processamento Reiniciado",
          description: "O processamento foi reiniciado com sucesso.",
        });
        startMonitoring();
      }
    } catch (error) {
      setIsProcessing(false);
      toast({
        title: "Erro ao Reiniciar",
        description: "Não foi possível reiniciar o processamento.",
        variant: "destructive",
      });
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'processing':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusText = (status?: string) => {
    switch (status) {
      case 'pending':
        return 'Aguardando';
      case 'processing':
        return 'Processando';
      case 'completed':
        return 'Concluído';
      case 'failed':
        return 'Falhou';
      default:
        return 'Não iniciado';
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-4">
      {/* Document Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Processamento de Documento Grande
          </CardTitle>
          <CardDescription>
            {fileName} ({fileSizeMB}MB)
            {shouldUseLargeProcessing && (
              <Badge variant="outline" className="ml-2">
                <AlertCircle className="h-3 w-3 mr-1" />
                Documento Grande
              </Badge>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getStatusIcon(processingJob?.status)}
              <span className="font-medium">Status:</span>
              <Badge className={getStatusColor(processingJob?.status)}>
                {getStatusText(processingJob?.status)}
              </Badge>
            </div>
            
            <div className="flex gap-2">
              {!processingJob || processingJob.status === 'failed' ? (
                <Button 
                  onClick={handleStartProcessing} 
                  disabled={isProcessing}
                  size="sm"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Iniciar Processamento
                </Button>
              ) : null}
              
              {processingJob?.status === 'failed' && (
                <Button 
                  onClick={handleRetryProcessing} 
                  disabled={isProcessing}
                  variant="outline"
                  size="sm"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Tentar Novamente
                </Button>
              )}
              
              {(processingJob?.status === 'processing' || processingJob?.status === 'pending') && (
                <Button 
                  onClick={handleCancelProcessing}
                  variant="destructive"
                  size="sm"
                >
                  <Square className="h-4 w-4 mr-2" />
                  Cancelar
                </Button>
              )}
            </div>
          </div>

          {/* Progress */}
          {processingJob && (processingJob.status === 'processing' || processingJob.status === 'pending') && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progresso</span>
                <span>{processingJob.progress}%</span>
              </div>
              <Progress value={processingJob.progress} className="h-2" />
              {processingJob.details && (
                <p className="text-sm text-muted-foreground">{processingJob.details}</p>
              )}
            </div>
          )}

          {/* Error Message */}
          {processingJob?.status === 'failed' && processingJob.error_message && (
            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>
                {processingJob.error_message}
              </AlertDescription>
            </Alert>
          )}

          {/* Processing Configuration */}
          {config && (
            <div className="bg-muted p-3 rounded-lg">
              <h4 className="font-medium mb-2">Configuração de Processamento</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>Páginas por lote: {config.maxPagesPerBatch || 50}</div>
                <div>Tamanho do chunk: {config.chunkSize || 800} palavras</div>
                <div>Sobreposição: {config.chunkOverlap || 100} palavras</div>
                <div>Análises paralelas: {config.maxConcurrentAnalysis || 3}</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Statistics Card */}
      {stats && processingJob?.status === 'completed' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Estatísticas do Processamento
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.totalChunks}</div>
                <div className="text-sm text-muted-foreground">Chunks Processados</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.confirmedLeads}</div>
                <div className="text-sm text-muted-foreground">Leads Confirmados</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{stats.alerts}</div>
                <div className="text-sm text-muted-foreground">Alertas</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{stats.totalPoints}</div>
                <div className="text-sm text-muted-foreground">Total de Pontos</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info Alert for Large Documents */}
      {shouldUseLargeProcessing && !processingJob && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Este documento é considerado grande ({fileSizeMB}MB). O processamento especializado 
            oferece melhor performance através de processamento em lotes e análise paralela.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default LargeDocumentProcessor;