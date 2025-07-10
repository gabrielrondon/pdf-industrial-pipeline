
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { SupabaseService } from '@/services/supabaseService';
import { DocumentAnalysis, DashboardStats } from '@/types';

export function useDocumentOperations() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const toggleDocumentPrivacy = async (id: string): Promise<DocumentAnalysis> => {
    if (!user?.id) {
      throw new Error('Usuário não autenticado');
    }

    setIsLoading(true);
    try {
      // Get the privacy toggle result
      const result = await SupabaseService.toggleDocumentPrivacy(id);

      // Track privacy change
      await SupabaseService.trackEvent(user.id, 'document_privacy_changed', {
        documentId: id,
        isPrivate: result.isPrivate
      });
      
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
  };

  const getStats = async (): Promise<DashboardStats> => {
    if (!user?.id) {
      throw new Error('Usuário não autenticado');
    }

    setIsLoading(true);
    try {
      const stats = await SupabaseService.getDashboardStats();
      
      // Track stats view
      await SupabaseService.trackEvent(user.id, 'dashboard_stats_viewed', {
        totalAnalyses: stats.totalAnalyses,
        validLeads: stats.validLeads
      });
      
      return stats;
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getCommunityLeads = async (): Promise<DocumentAnalysis[]> => {
    if (!user?.id) {
      throw new Error('Usuário não autenticado');
    }

    if (user.plan !== 'premium') {
      throw new Error('Acesso restrito a usuários Premium');
    }

    setIsLoading(true);
    try {
      const communityLeads = await SupabaseService.getCommunityLeads();
      
      // Track community access
      await SupabaseService.trackEvent(user.id, 'community_leads_accessed', {
        leadsCount: communityLeads.length
      });
      
      return communityLeads;
    } catch (error) {
      console.error('Error fetching community leads:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return { 
    toggleDocumentPrivacy, 
    getStats, 
    getCommunityLeads, 
    isLoading 
  };
}
