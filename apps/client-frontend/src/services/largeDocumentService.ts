import { supabase } from '@/integrations/supabase/client';

export interface ProcessingConfig {
  maxPagesPerBatch?: number;
  chunkSize?: number;
  chunkOverlap?: number;
  maxConcurrentAnalysis?: number;
  analysisTimeout?: number;
}

export interface ProcessingJob {
  id: string;
  document_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  details?: string;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface LargeDocumentResult {
  success: boolean;
  documentId: string;
  model: string;
  batches: number;
  totalPages: number;
  totalPoints: number;
  confirmedLeads: number;
  processingTime?: string;
}

class LargeDocumentService {
  
  /**
   * Determines if a document should use large document processing
   */
  static shouldUseLargeProcessing(fileSize: number, estimatedPages?: number): boolean {
    const SIZE_THRESHOLD = 10 * 1024 * 1024; // 10MB
    const PAGES_THRESHOLD = 100; // 100 pages
    
    return fileSize > SIZE_THRESHOLD || (estimatedPages && estimatedPages > PAGES_THRESHOLD);
  }

  /**
   * Starts large document processing
   */
  static async startProcessing(
    documentId: string,
    fileUrl: string,
    model: string = 'native',
    documentType: string = 'edital',
    config?: ProcessingConfig
  ): Promise<{ jobId: string; success: boolean }> {
    try {
      console.log(`Starting large document processing for ${documentId}`);

      // Create processing job in database
      const { data: jobData, error: jobError } = await supabase
        .rpc('start_large_document_processing', {
          p_document_id: documentId,
          p_config: config || {}
        });

      if (jobError) {
        console.error('Failed to create processing job:', jobError);
        throw new Error(`Failed to create processing job: ${jobError.message}`);
      }

      const jobId = jobData;

      // Call the large document processing Edge Function
      const { data, error } = await supabase.functions.invoke('process-large-document', {
        body: {
          documentId,
          fileUrl,
          model,
          documentType,
          config
        }
      });

      if (error) {
        console.error('Large document processing failed:', error);
        throw new Error(`Processing failed: ${error.message}`);
      }

      console.log('Large document processing started successfully:', data);
      return { jobId, success: true };

    } catch (error) {
      console.error('Error starting large document processing:', error);
      throw error;
    }
  }

  /**
   * Gets the current processing status for a document
   */
  static async getProcessingStatus(documentId: string): Promise<ProcessingJob | null> {
    try {
      const { data, error } = await supabase
        .rpc('get_document_processing_status', {
          p_document_id: documentId
        });

      if (error) {
        console.error('Failed to get processing status:', error);
        return null;
      }

      return data?.[0] || null;
    } catch (error) {
      console.error('Error getting processing status:', error);
      return null;
    }
  }

  /**
   * Monitors processing progress with real-time updates
   */
  static async monitorProcessing(
    documentId: string,
    onProgress: (job: ProcessingJob) => void,
    onComplete: (result: ProcessingJob) => void,
    onError: (error: string) => void
  ): Promise<() => void> {
    let isMonitoring = true;
    let pollInterval: NodeJS.Timeout;

    const poll = async () => {
      if (!isMonitoring) return;

      try {
        const status = await this.getProcessingStatus(documentId);
        
        if (status) {
          onProgress(status);

          if (status.status === 'completed') {
            isMonitoring = false;
            if (pollInterval) clearInterval(pollInterval);
            onComplete(status);
          } else if (status.status === 'failed') {
            isMonitoring = false;
            if (pollInterval) clearInterval(pollInterval);
            onError(status.error_message || 'Processing failed');
          }
        }
      } catch (error) {
        console.error('Error polling processing status:', error);
        onError('Failed to check processing status');
      }
    };

    // Initial poll
    await poll();

    // Set up polling interval
    if (isMonitoring) {
      pollInterval = setInterval(poll, 2000); // Poll every 2 seconds
    }

    // Return cleanup function
    return () => {
      isMonitoring = false;
      if (pollInterval) clearInterval(pollInterval);
    };
  }

  /**
   * Gets chunk summaries for a document
   */
  static async getChunkSummaries(documentId: string) {
    try {
      const { data, error } = await supabase
        .from('chunk_summaries')
        .select('*')
        .eq('document_id', documentId)
        .order('created_at', { ascending: true });

      if (error) {
        console.error('Failed to get chunk summaries:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Error getting chunk summaries:', error);
      return [];
    }
  }

  /**
   * Gets analysis points with chunk information
   */
  static async getAnalysisPointsWithChunks(documentId: string) {
    try {
      const { data, error } = await supabase
        .from('analysis_points')
        .select('*')
        .eq('document_id', documentId)
        .order('page', { ascending: true });

      if (error) {
        console.error('Failed to get analysis points:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Error getting analysis points:', error);
      return [];
    }
  }

  /**
   * Cancels an ongoing processing job
   */
  static async cancelProcessing(documentId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('processing_jobs')
        .update({ 
          status: 'failed',
          error_message: 'Cancelled by user',
          completed_at: new Date().toISOString()
        })
        .eq('document_id', documentId);

      if (error) {
        console.error('Failed to cancel processing:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error cancelling processing:', error);
      return false;
    }
  }

  /**
   * Retries failed processing
   */
  static async retryProcessing(
    documentId: string,
    fileUrl: string,
    model: string = 'native',
    documentType: string = 'edital',
    config?: ProcessingConfig
  ): Promise<{ jobId: string; success: boolean }> {
    try {
      // Reset the processing job
      await supabase
        .from('processing_jobs')
        .update({
          status: 'pending',
          progress: 0,
          details: null,
          error_message: null,
          started_at: null,
          completed_at: null
        })
        .eq('document_id', documentId);

      // Start processing again
      return await this.startProcessing(documentId, fileUrl, model, documentType, config);
    } catch (error) {
      console.error('Error retrying processing:', error);
      throw error;
    }
  }

  /**
   * Gets processing statistics
   */
  static async getProcessingStats(documentId: string) {
    try {
      const [chunksResult, pointsResult, summariesResult] = await Promise.all([
        supabase
          .from('document_chunks')
          .select('id', { count: 'exact' })
          .eq('document_id', documentId),
        
        supabase
          .from('analysis_points')
          .select('status', { count: 'exact' })
          .eq('document_id', documentId),
        
        supabase
          .from('chunk_summaries')
          .select('id', { count: 'exact' })
          .eq('document_id', documentId)
      ]);

      const totalChunks = chunksResult.count || 0;
      const totalPoints = pointsResult.count || 0;
      const totalSummaries = summariesResult.count || 0;

      // Get status breakdown
      const { data: statusData } = await supabase
        .from('analysis_points')
        .select('status')
        .eq('document_id', documentId);

      const statusCounts = statusData?.reduce((acc: any, point: any) => {
        acc[point.status] = (acc[point.status] || 0) + 1;
        return acc;
      }, {}) || {};

      return {
        totalChunks,
        totalPoints,
        totalSummaries,
        confirmedLeads: statusCounts.confirmado || 0,
        alerts: statusCounts.alerta || 0,
        notIdentified: statusCounts['não identificado'] || 0
      };
    } catch (error) {
      console.error('Error getting processing stats:', error);
      return {
        totalChunks: 0,
        totalPoints: 0,
        totalSummaries: 0,
        confirmedLeads: 0,
        alerts: 0,
        notIdentified: 0
      };
    }
  }
}

export default LargeDocumentService;