import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  RefreshCw,
  AlertCircle,
  Play
} from 'lucide-react';
import LargeDocumentService, { ProcessingJob } from '@/services/largeDocumentService';
import { useToast } from '@/hooks/use-toast';

interface LargeDocumentStatusProps {
  documentId: string;
  fileName: string;
  fileSize?: number;
  onProcessingComplete?: () => void;
}

const LargeDocumentStatus: React.FC<LargeDocumentStatusProps> = ({
  documentId,
  fileName,
  fileSize,
  onProcessingComplete
}) => {
  const [processingJob, setProcessingJob] = useState<ProcessingJob | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadStatus();
  }, [documentId]);

  useEffect(() => {
    if (processingJob && (processingJob.status === 'processing' || processingJob.status === 'pending')) {
      const cleanup = LargeDocumentService.monitorProcessing(
        documentId,
        (job) => setProcessingJob(job),
        (result) => {
          setProcessingJob(result);
          if (onProcessingComplete) onProcessingComplete();
        },
        (error) => {
          toast({
            title: "Erro no Processamento",
            description: error,
            variant: "destructive",
          });
        }
      );

      return () => {
        cleanup.then(fn => fn());
      };
    }
  }, [processingJob?.status, documentId, onProcessingComplete, toast]);

  const loadStatus = async () => {
    try {
      const status = await LargeDocumentService.getProcessingStatus(documentId);
      setProcessingJob(status);
    } catch (error) {
      console.error('Failed to load processing status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = async () => {
    try {
      // Note: This would need the file URL which we don't have here
      // In a real implementation, we'd need to store this or get it from the document record
      toast({
        title: "Funcionalidade em Desenvolvimento",
        description: "Retry será implementado em breve. Por favor, faça upload novamente.",
        variant: "default",
      });
    } catch (error) {
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
        return 'Aguardando Processamento';
      case 'processing':
        return 'Processando';
      case 'completed':
        return 'Processamento Concluído';
      case 'failed':
        return 'Processamento Falhou';
      default:
        return 'Status Desconhecido';
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

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <RefreshCw className="h-4 w-4 animate-spin" />
        Carregando status...
      </div>
    );
  }

  if (!processingJob) {
    return null;
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {getStatusIcon(processingJob.status)}
          <Badge className={getStatusColor(processingJob.status)}>
            {getStatusText(processingJob.status)}
          </Badge>
          {fileSize && (
            <span className="text-xs text-muted-foreground">
              ({(fileSize / (1024 * 1024)).toFixed(2)}MB)
            </span>
          )}
        </div>
        
        {processingJob.status === 'failed' && (
          <Button onClick={handleRetry} size="sm" variant="outline">
            <RefreshCw className="h-3 w-3 mr-1" />
            Tentar Novamente
          </Button>
        )}
      </div>

      {/* Progress bar for active processing */}
      {(processingJob.status === 'processing' || processingJob.status === 'pending') && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span>Progresso</span>
            <span>{processingJob.progress}%</span>
          </div>
          <Progress value={processingJob.progress} className="h-1" />
          {processingJob.details && (
            <p className="text-xs text-muted-foreground">{processingJob.details}</p>
          )}
        </div>
      )}

      {/* Error message */}
      {processingJob.status === 'failed' && processingJob.error_message && (
        <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
          {processingJob.error_message}
        </div>
      )}

      {/* Completion info */}
      {processingJob.status === 'completed' && (
        <div className="text-xs text-green-600 bg-green-50 p-2 rounded">
          Processamento concluído com sucesso! Os resultados estão disponíveis.
        </div>
      )}
    </div>
  );
};

export default LargeDocumentStatus;