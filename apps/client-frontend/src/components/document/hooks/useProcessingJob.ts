
import { useState, useEffect } from 'react';
import { railwayApi } from '@/services/railwayApiService';

interface ProcessingJob {
  id: string;
  document_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

interface UseProcessingJobProps {
  documentId: string;
  onProcessingComplete?: () => void;
}

export function useProcessingJob({ documentId, onProcessingComplete }: UseProcessingJobProps) {
  const [job, setJob] = useState<ProcessingJob | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchJobStatus = async () => {
    try {
      console.log('🔍 Fetching job status for document:', documentId);
      
      // Buscar status do job via Railway API
      const jobData = await railwayApi.getJobStatus(documentId);
      
      if (jobData) {
        // Transformar dados da Railway para o formato esperado
        const processingJob: ProcessingJob = {
          id: jobData.job_id || documentId,
          document_id: documentId,
          status: jobData.status as any,
          progress: jobData.progress || (jobData.status === 'completed' ? 100 : 50),
          error_message: jobData.error,
          created_at: jobData.created_at || new Date().toISOString(),
          completed_at: jobData.status === 'completed' ? new Date().toISOString() : undefined
        };
        
        setJob(processingJob);
        
        // Check if processing is complete
        if (jobData.status === 'completed' && onProcessingComplete) {
          onProcessingComplete();
        }
      } else {
        // Se não encontrou job específico, criar um job "completed" genérico
        const defaultJob: ProcessingJob = {
          id: documentId,
          document_id: documentId,
          status: 'completed',
          progress: 100,
          created_at: new Date().toISOString(),
          completed_at: new Date().toISOString()
        };
        
        setJob(defaultJob);
      }
    } catch (error) {
      console.error('Error fetching job status:', error);
      
      // Em caso de erro, assumir que o documento está "completed"
      const fallbackJob: ProcessingJob = {
        id: documentId,
        document_id: documentId,
        status: 'completed',
        progress: 100,
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString()
      };
      
      setJob(fallbackJob);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobStatus();
    
    // Opcional: polling para atualizar status periodicamente
    const interval = setInterval(() => {
      if (job?.status === 'pending' || job?.status === 'processing') {
        fetchJobStatus();
      }
    }, 5000); // Check a cada 5 segundos se ainda em processamento

    return () => {
      clearInterval(interval);
    };
  }, [documentId, onProcessingComplete, job?.status]);

  return { job, isLoading };
}
