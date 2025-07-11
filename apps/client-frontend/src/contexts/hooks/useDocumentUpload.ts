
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { DocumentAnalysis, DocumentType } from '@/types';
import { AIModel } from '@/components/document/ModelSelector';
import { railwayApi } from '@/services/railwayApiService';
import { transformRailwayResultsToDocumentAnalysis } from '@/utils/dataTransformers';

export function useDocumentUpload() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const uploadDocument = async (file: File, analysisModel: AIModel = 'native'): Promise<DocumentAnalysis> => {
    if (!user?.id) {
      throw new Error('Usuário não autenticado');
    }

    setIsLoading(true);
    
    try {
      console.log('🚂 Uploading document via Railway API...');
      
      // Upload and process via Railway API with user ID
      const uploadResult = await railwayApi.uploadDocument(file, user.id);
      
      if (!uploadResult.success) {
        throw new Error(uploadResult.error || 'Upload failed');
      }

      // If we have a job_id, monitor the processing
      if (uploadResult.job_id) {
        console.log('📡 Monitoring job:', uploadResult.job_id);
        
        // Poll for completion (simplified version)
        let attempts = 0;
        const maxAttempts = 30; // 2.5 minutes max
        
        while (attempts < maxAttempts) {
          const jobStatus = await railwayApi.getJobStatus(uploadResult.job_id);
          
          if (jobStatus.status === 'completed') {
            // Transform Railway results to DocumentAnalysis format
            return transformRailwayResultsToDocumentAnalysis(
              jobStatus.results || jobStatus,
              uploadResult.job_id,
              file.name
            );
          }
          
          if (jobStatus.status === 'failed') {
            throw new Error(jobStatus.error || 'Processing failed');
          }
          
          // Wait 5 seconds before next check
          await new Promise(resolve => setTimeout(resolve, 5000));
          attempts++;
        }
        
        throw new Error('Processing timeout - job taking too long');
      }

      // If no job tracking, create a basic document analysis
      return {
        id: uploadResult.job_id || 'temp-' + Date.now(),
        userId: user.id,
        fileName: file.name,
        fileUrl: '',
        type: determineDocumentType(file.name),
        uploadedAt: new Date().toISOString(),
        analyzedAt: new Date().toISOString(),
        isPrivate: false,
        points: []
      };

    } catch (error) {
      console.error('❌ Railway upload error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return { uploadDocument, isLoading };
}

// Helper function
function determineDocumentType(filename: string): DocumentType {
  const name = filename.toLowerCase();
  if (name.includes('edital')) return 'edital';
  if (name.includes('processo')) return 'processo';
  if (name.includes('laudo')) return 'laudo';
  return 'outro';
}
