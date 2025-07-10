
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { SupabaseService } from '@/services/supabaseService';
import { DocumentAnalysis } from '@/types';

export function useDocumentState() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<DocumentAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load user documents on mount and user change
  useEffect(() => {
    if (user?.id) {
      refreshDocuments();
    }
  }, [user?.id]);

  const refreshDocuments = async () => {
    if (!user?.id) return;
    
    setIsLoading(true);
    try {
      const userDocuments = await SupabaseService.getUserDocuments(user.id);
      setDocuments(userDocuments);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getDocumentById = (id: string): DocumentAnalysis | undefined => {
    return documents.find(doc => doc.id === id);
  };

  const addDocument = (document: DocumentAnalysis) => {
    setDocuments(prev => [document, ...prev]);
  };

  const updateDocument = (id: string, updates: Partial<DocumentAnalysis>) => {
    setDocuments(prev => prev.map(doc => 
      doc.id === id ? { ...doc, ...updates } : doc
    ));
  };

  return {
    documents,
    isLoading,
    refreshDocuments,
    getDocumentById,
    addDocument,
    updateDocument
  };
}
