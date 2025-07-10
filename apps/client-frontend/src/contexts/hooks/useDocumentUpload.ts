
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { SupabaseService } from '@/services/supabaseService';
import { supabase } from '@/integrations/supabase/client';
import { DocumentAnalysis, DocumentType } from '@/types';
import { AIModel } from '@/components/document/ModelSelector';
import { UploadDocumentParams, DocumentUploadResult } from '../types/documentTypes';

export function useDocumentUpload() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const uploadDocument = async (file: File, analysisModel: AIModel = 'native'): Promise<DocumentAnalysis> => {
    if (!user?.id) {
      throw new Error('Usuário não autenticado');
    }

    setIsLoading(true);
    const startTime = Date.now();
    
    try {
      // Track upload event
      await SupabaseService.trackEvent(user.id, 'document_upload_started', {
        fileName: file.name,
        fileSize: file.size,
        analysisModel
      });

      // Upload file to storage
      const fileUrl = await SupabaseService.uploadDocument(file, user.id);
      
      // Determine document type
      const documentType: DocumentType = 
        file.name.toLowerCase().includes('edital') ? 'edital' :
        file.name.toLowerCase().includes('processo') ? 'processo' :
        file.name.toLowerCase().includes('laudo') ? 'laudo' : 'outro';

      // Call edge function for analysis
      const formData = new FormData();
      formData.append('file', file);
      formData.append('model', analysisModel);
      formData.append('documentType', documentType);

      const response = await supabase.functions.invoke('analyze-document', {
        body: formData
      });

      if (response.error) {
        throw new Error(response.error.message);
      }

      const analysisResult = response.data;
      const analysisDurationMs = Date.now() - startTime;

      // Save document to database
      const documentId = await SupabaseService.saveDocumentAnalysis(
        user.id,
        file.name,
        fileUrl,
        file.size,
        file.type,
        analysisModel,
        analysisDurationMs,
        documentType,
        user.plan === 'free' ? false : true
      );

      // Save analysis points and leads
      await SupabaseService.saveAnalysisPoints(documentId, analysisResult.points);
      await SupabaseService.saveLeads(documentId, user.id, analysisResult.points);

      // Track completion
      await SupabaseService.trackEvent(user.id, 'document_analysis_completed', {
        documentId,
        pointsCount: analysisResult.points.length,
        analysisDurationMs,
        analysisModel
      });

      const newDocument: DocumentAnalysis = {
        id: documentId,
        userId: user.id,
        fileName: file.name,
        fileUrl,
        type: documentType,
        uploadedAt: new Date().toISOString(),
        analyzedAt: new Date().toISOString(),
        isPrivate: user.plan === 'free' ? false : true,
        points: analysisResult.points
      };

      return newDocument;
    } catch (error) {
      console.error('Error uploading document:', error);
      
      // Track error
      await SupabaseService.trackEvent(user.id, 'document_upload_error', {
        error: error instanceof Error ? error.message : 'Unknown error',
        fileName: file.name
      });
      
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return { uploadDocument, isLoading };
}
