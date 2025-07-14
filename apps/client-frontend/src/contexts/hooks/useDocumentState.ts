
import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { SupabaseService } from '@/services/supabaseService';
import { DocumentAnalysis } from '@/types';

export function useDocumentState() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<DocumentAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const loadingRef = useRef(false);

  const refreshDocuments = useCallback(async () => {
    if (!user?.id) {
      console.log('❌ Usuário não autenticado, não é possível carregar documentos');
      return;
    }
    
    // Prevenir chamadas múltiplas simultâneas
    if (loadingRef.current) {
      console.log('⏳ refreshDocuments já está executando, ignorando...');
      return;
    }
    
    console.log('🔄 Iniciando carregamento de documentos para usuário:', user.id);
    loadingRef.current = true;
    setIsLoading(true);
    
    try {
      const userDocuments = await SupabaseService.getUserDocuments(user.id);
      console.log('📋 Documentos carregados no contexto:', userDocuments.length);
      setDocuments(userDocuments);
    } catch (error) {
      console.error('❌ Erro no contexto ao carregar documentos:', error);
      // Em caso de erro, não limpar documentos existentes
    } finally {
      setIsLoading(false);
      loadingRef.current = false;
    }
  }, [user?.id]);

  // Load user documents on mount and user change
  useEffect(() => {
    if (user?.id && refreshDocuments) {
      console.log('📋 useDocumentState: user.id mudou para:', user.id);
      refreshDocuments();
    } else if (!user?.id) {
      console.log('📋 useDocumentState: user.id é null, limpando documentos');
      setDocuments([]);
    }
  }, [user?.id]); // Remove refreshDocuments from deps since it already depends on user?.id

  const getDocumentById = useCallback((id: string): DocumentAnalysis | undefined => {
    return documents.find(doc => doc.id === id);
  }, [documents]);

  const addDocument = useCallback((document: DocumentAnalysis) => {
    setDocuments(prev => [document, ...prev]);
  }, []);

  const updateDocument = useCallback((id: string, updates: Partial<DocumentAnalysis>) => {
    setDocuments(prev => prev.map(doc => 
      doc.id === id ? { ...doc, ...updates } : doc
    ));
  }, []);

  return {
    documents,
    isLoading,
    refreshDocuments,
    getDocumentById,
    addDocument,
    updateDocument
  };
}
