
import { supabase } from '@/integrations/supabase/client';
import { DocumentAnalysis, DashboardStats } from '@/types';

export interface Lead {
  id: string;
  document_id: string;
  user_id: string;
  title: string;
  description?: string;
  risk_level: 'high' | 'medium' | 'low';
  category: string;
  value_estimate?: number;
  location?: string;
  auction_date?: string;
  status: 'active' | 'expired' | 'sold' | 'cancelled';
  contact_info?: any;
  metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface AnalyticsEvent {
  event_type: string;
  event_data?: any;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  word_count: number;
  page_start?: number;
  page_end?: number;
  created_at: string;
}

export interface ProcessingJob {
  id: string;
  document_id: string;
  user_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

const SHARE_CREDIT_REWARD = 5; // Créditos ganhos por compartilhar um lead

export class SupabaseService {
  // Upload document to storage
  static async uploadDocument(file: File, userId: string): Promise<string> {
    const fileName = `${userId}/${Date.now()}-${file.name}`;
    
    const { data, error } = await supabase.storage
      .from('documents')
      .upload(fileName, file);
    
    if (error) {
      console.error('Error uploading file:', error);
      throw new Error(`Erro ao fazer upload: ${error.message}`);
    }
    
    const { data: publicUrl } = supabase.storage
      .from('documents')
      .getPublicUrl(fileName);
    
    return publicUrl.publicUrl;
  }

  // Save document analysis to database
  static async saveDocumentAnalysis(
    userId: string,
    fileName: string,
    fileUrl: string,
    fileSize: number,
    mimeType: string,
    analysisModel: string,
    analysisDurationMs: number,
    documentType: 'edital' | 'processo' | 'laudo' | 'outro',
    isPrivate: boolean = false
  ): Promise<string> {
    const { data, error } = await supabase
      .from('documents')
      .insert({
        user_id: userId,
        file_name: fileName,
        file_url: fileUrl,
        type: documentType,
        is_private: isPrivate
      } as any)
      .select('id')
      .single();
    
    if (error) {
      console.error('Error saving document:', error);
      throw new Error(`Erro ao salvar documento: ${error.message}`);
    }
    
    return data?.id;
  }

  // Save analysis points
  static async saveAnalysisPoints(documentId: string, points: any[]): Promise<void> {
    const analysisPoints = points.map(point => ({
      document_id: documentId,
      title: point.title,
      comment: point.comment,
      status: point.status
    }));

    const { error } = await supabase
      .from('analysis_points')
      .insert(analysisPoints as any);
    
    if (error) {
      console.error('Error saving analysis points:', error);
      throw new Error(`Erro ao salvar pontos de análise: ${error.message}`);
    }
  }

  // Get document chunks using direct fetch to avoid type issues
  static async getDocumentChunks(documentId: string): Promise<DocumentChunk[]> {
    try {
      const session = await supabase.auth.getSession();
      const response = await fetch(`https://rjbiyndpxqaallhjmbwm.supabase.co/rest/v1/document_chunks?document_id=eq.${documentId}&order=chunk_index`, {
        headers: {
          'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYml5bmRweHFhYWxsaGptYndtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2NjEwNzUsImV4cCI6MjA2MTIzNzA3NX0.h3hviSaTY6fJLUrRbl2X6LHfQlxAhHishQ-jVur09-A',
          'Authorization': `Bearer ${session.data.session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error('Error fetching document chunks');
        return [];
      }

      const data = await response.json();
      return data || [];
    } catch (error) {
      console.error('Error fetching document chunks:', error);
      return [];
    }
  }

  // Get processing job status using direct fetch
  static async getProcessingJob(documentId: string): Promise<ProcessingJob | null> {
    try {
      const session = await supabase.auth.getSession();
      const response = await fetch(`https://rjbiyndpxqaallhjmbwm.supabase.co/rest/v1/processing_jobs?document_id=eq.${documentId}&order=created_at.desc&limit=1`, {
        headers: {
          'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYml5bmRweHFhYWxsaGptYndtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2NjEwNzUsImV4cCI6MjA2MTIzNzA3NX0.h3hviSaTY6fJLUrRbl2X6LHfQlxAhHishQ-jVur09-A',
          'Authorization': `Bearer ${session.data.session?.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error('Error fetching processing job');
        return null;
      }

      const data = await response.json();
      if (data && data.length > 0) {
        return data[0] as ProcessingJob;
      }

      return null;
    } catch (error) {
      console.error('Error fetching processing job:', error);
      return null;
    }
  }

  // Start semantic search
  static async semanticSearch(
    query: string, 
    documentIds?: string[], 
    limit = 10, 
    threshold = 0.7
  ): Promise<any> {
    const { data, error } = await supabase.functions.invoke('semantic-search', {
      body: {
        query,
        documentIds,
        limit,
        threshold
      }
    });

    if (error) {
      console.error('Error in semantic search:', error);
      throw new Error(`Erro na busca semântica: ${error.message}`);
    }

    return data;
  }

  // Save leads automatically
  static async saveLeads(documentId: string, userId: string, points: any[]): Promise<void> {
    // This would use a direct RPC call when leads table is properly set up
    console.log('Leads would be saved:', { documentId, userId, pointsCount: points.length });
  }

  // Track analytics
  static async trackEvent(userId: string, eventType: string, eventData?: any): Promise<void> {
    // This would use a direct RPC call when analytics table is properly set up
    console.log('Analytics event:', { userId, eventType, eventData });
  }

  // Toggle document privacy and handle credit rewards
  static async toggleDocumentPrivacy(documentId: string): Promise<{ success: boolean; isPrivate: boolean; creditsEarned?: number }> {
    const { data, error } = await supabase.functions.invoke('toggle-document-privacy', {
      body: { documentId }
    });

    if (error) {
      console.error('Error toggling privacy:', error);
      throw new Error(error.message);
    }

    if (!data.success) {
      throw new Error(data.error || 'Erro ao alterar privacidade');
    }

    const newPrivacyState = data.is_private as boolean;

    // If document became public, reward user with credits
    if (!newPrivacyState) {
      try {
        const { error: creditError } = await supabase.functions.invoke('manage-credits', {
          body: {
            action: 'earn',
            amount: SHARE_CREDIT_REWARD,
            reason: 'Compartilhamento de lead público',
            documentId: documentId
          }
        });

        if (creditError) {
          console.error('Error awarding credits:', creditError);
        }

        return { success: true, isPrivate: newPrivacyState, creditsEarned: SHARE_CREDIT_REWARD };
      } catch (err) {
        console.error('Error awarding credits:', err);
        return { success: true, isPrivate: newPrivacyState };
      }
    }

    return { success: true, isPrivate: newPrivacyState };
  }

  // Get user documents
  static async getUserDocuments(userId: string): Promise<DocumentAnalysis[]> {
    const { data: documents, error: docError } = await supabase
      .from('documents')
      .select('*')
      .eq('user_id', userId)
      .order('analyzed_at', { ascending: false });
    
    if (docError) {
      console.error('Error fetching documents:', docError);
      return [];
    }

    const documentsWithPoints = await Promise.all(
      (documents || []).map(async (doc) => {
        const { data: points } = await supabase
          .from('analysis_points')
          .select('*')
          .eq('document_id', doc.id);
        
        return {
          id: doc.id,
          userId: doc.user_id,
          fileName: doc.file_name,
          fileUrl: doc.file_url,
          type: doc.type,
          uploadedAt: doc.uploaded_at,
          analyzedAt: doc.analyzed_at,
          isPrivate: doc.is_private,
          points: points || []
        };
      })
    );

    return documentsWithPoints;
  }

  // Get dashboard stats - usando dados reais do Supabase
  static async getDashboardStats(): Promise<DashboardStats> {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Usuário não autenticado');

      // Buscar dados do perfil para créditos
      const { data: profile } = await supabase
        .from('profiles')
        .select('credits')
        .eq('id', user.id)
        .single();

      // Buscar documentos do usuário
      const { data: documents, error: docsError } = await supabase
        .from('documents')
        .select('id, type')
        .eq('user_id', user.id);

      if (docsError) {
        console.error('Error fetching documents:', docsError);
        return this.getDefaultStats(profile?.credits || 100);
      }

      const totalAnalyses = documents?.length || 0;

      // Distribuição de tipos de documento
      const documentTypes = documents?.reduce((acc: any[], doc) => {
        const existing = acc.find(item => item.type === doc.type);
        if (existing) {
          existing.count++;
        } else {
          acc.push({ type: doc.type, count: 1 });
        }
        return acc;
      }, []) || [];

      // Buscar pontos de análise para distribuição de status
      const documentIds = documents?.map(d => d.id) || [];
      
      let statusDistribution: any[] = [];
      let commonIssues: any[] = [];
      let validLeads = 0;
      
      if (documentIds.length > 0) {
        const { data: points } = await supabase
          .from('analysis_points')
          .select('status, title')
          .in('document_id', documentIds);

        statusDistribution = points?.reduce((acc: any[], point) => {
          const existing = acc.find(item => item.status === point.status);
          if (existing) {
            existing.count++;
          } else {
            acc.push({ status: point.status, count: 1 });
          }
          return acc;
        }, []) || [];

        validLeads = statusDistribution.find(s => s.status === 'confirmado')?.count || 0;

        commonIssues = points?.filter(p => p.status === 'alerta')
          .reduce((acc: any[], point) => {
            const existing = acc.find(item => item.issue === point.title);
            if (existing) {
              existing.count++;
            } else {
              acc.push({ issue: point.title || 'Problema geral', count: 1 });
            }
            return acc;
          }, [])
          .slice(0, 5) || [];
      }

      // Buscar documentos compartilhados (não privados)
      const { data: sharedDocs } = await supabase
        .from('documents')
        .select('id')
        .eq('user_id', user.id)
        .eq('is_private', false);

      const sharedLeads = sharedDocs?.length || 0;

      return {
        totalAnalyses,
        validLeads,
        sharedLeads,
        credits: profile?.credits || 100,
        documentTypes,
        statusDistribution,
        commonIssues
      };
    } catch (error) {
      console.error('Error getting dashboard stats:', error);
      return this.getDefaultStats(100);
    }
  }

  private static getDefaultStats(credits: number = 100): DashboardStats {
    return {
      totalAnalyses: 0,
      validLeads: 0,
      sharedLeads: 0,
      credits,
      documentTypes: [],
      statusDistribution: [],
      commonIssues: []
    };
  }

  // Get community leads (for premium users) - simplified version
  static async getCommunityLeads(): Promise<DocumentAnalysis[]> {
    const { data: documents, error } = await supabase
      .from('documents')
      .select('*')
      .eq('is_private', false)
      .order('analyzed_at', { ascending: false })
      .limit(20);
    
    if (error) {
      console.error('Error fetching community leads:', error);
      return [];
    }

    return documents?.map(doc => ({
      id: doc.id,
      userId: doc.user_id,
      fileName: doc.file_name,
      fileUrl: doc.file_url,
      type: doc.type,
      uploadedAt: doc.uploaded_at,
      analyzedAt: doc.analyzed_at,
      isPrivate: doc.is_private,
      points: []
    })) || [];
  }

  // Get user profile from profiles table
  static async getUserProfile(userId: string) {
    const { data, error } = await supabase
      .from('profiles')
      .select(
        'id, email, name, plan, credits, credits_used, credits_earned, created_at'
      )
      .eq('id', userId)
      .single();

    if (error) {
      console.error('Error fetching profile:', error);
      return null;
    }

    return {
      id: data.id,
      email: data.email,
      name: data.name ?? undefined,
      plan: data.plan,
      credits: data.credits,
      credits_used: data.credits_used,
      credits_earned: data.credits_earned,
      createdAt: data.created_at
    } as const;
  }

  // Update user profile name
  static async updateUserProfile(userId: string, name: string) {
    const { error } = await supabase
      .from('profiles')
      .update({ name })
      .eq('id', userId);

    if (error) {
      console.error('Error updating profile:', error);
      throw new Error('Falha ao atualizar perfil');
    }

    // Also update auth user metadata
    const { error: authError } = await supabase.auth.updateUser({
      data: { name }
    });
    if (authError) {
      console.error('Error updating auth metadata:', authError);
    }
  }
}
