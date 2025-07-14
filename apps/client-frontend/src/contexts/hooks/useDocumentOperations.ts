
import { useState, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { SupabaseService } from '@/services/supabaseService';
import { DocumentAnalysis, DashboardStats } from '@/types';

export function useDocumentOperations() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const toggleDocumentPrivacy = useCallback(async (id: string): Promise<DocumentAnalysis> => {
    if (!user?.id) {
      throw new Error('Usuário não autenticado');
    }

    setIsLoading(true);
    try {
      // Get the privacy toggle result
      const result = await SupabaseService.toggleDocumentPrivacy(id);

      // Track privacy change - DEPRECATED: trackEvent now handled by Railway
      console.log('🔄 Document privacy changed:', { documentId: id, isPrivate: result.isPrivate });
      
      // Since we need to return a DocumentAnalysis, we need to fetch the updated document
      // For now, we'll create a minimal DocumentAnalysis with the updated privacy state
      // The calling code should handle updating the document state properly
      const updatedDocument: DocumentAnalysis = {
        id,
        userId: user.id,
        fileName: '', // These will be updated by the calling code
        fileUrl: '',
        type: 'outro',
        uploadedAt: new Date().toISOString(),
        analyzedAt: new Date().toISOString(),
        isPrivate: result.isPrivate,
        points: []
      };
      
      return updatedDocument;
    } catch (error) {
      console.error('Error toggling document privacy:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user?.id]);

  const getStats = useCallback(async (): Promise<DashboardStats> => {
    if (!user?.id) {
      throw new Error('Usuário não autenticado');
    }

    setIsLoading(true);
    try {
      const stats = await SupabaseService.getDashboardStats();
      
      // Track stats view - DEPRECATED: trackEvent now handled by Railway
      console.log('📊 Dashboard stats viewed:', { totalAnalyses: stats.totalAnalyses, validLeads: stats.validLeads });
      
      return stats;
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user?.id]);

  const getCommunityLeads = useCallback(async (): Promise<DocumentAnalysis[]> => {
    if (!user?.id) {
      throw new Error('Usuário não autenticado');
    }

    if (user.plan !== 'premium') {
      throw new Error('Acesso restrito a usuários Premium');
    }

    setIsLoading(true);
    try {
      const communityLeads = await SupabaseService.getCommunityLeads();
      
      // Track community access - DEPRECATED: trackEvent now handled by Railway
      console.log('👥 Community leads accessed:', { leadsCount: communityLeads.length });
      
      return communityLeads;
    } catch (error) {
      console.error('Error fetching community leads:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user?.id, user?.plan]);

  return { 
    toggleDocumentPrivacy, 
    getStats, 
    getCommunityLeads, 
    isLoading 
  };
}
