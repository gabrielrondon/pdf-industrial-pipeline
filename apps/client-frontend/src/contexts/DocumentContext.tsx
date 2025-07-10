
import { createContext, useContext, ReactNode } from 'react';
import { DocumentAnalysis } from '@/types';
import { AIModel } from '@/components/document/ModelSelector';
import { DocumentContextType } from './types/documentTypes';
import { useDocumentState } from './hooks/useDocumentState';
import { useDocumentUpload } from './hooks/useDocumentUpload';
import { useDocumentOperations } from './hooks/useDocumentOperations';

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const DocumentProvider = ({ children }: { children: ReactNode }) => {
  const { 
    documents, 
    isLoading: stateLoading, 
    refreshDocuments, 
    getDocumentById, 
    addDocument, 
    updateDocument 
  } = useDocumentState();
  
  const { 
    uploadDocument: uploadDocumentHook, 
    isLoading: uploadLoading 
  } = useDocumentUpload();
  
  const { 
    toggleDocumentPrivacy: togglePrivacyHook, 
    getStats, 
    getCommunityLeads, 
    isLoading: operationsLoading 
  } = useDocumentOperations();

  const isLoading = stateLoading || uploadLoading || operationsLoading;

  const uploadDocument = async (file: File, analysisModel: AIModel = 'native'): Promise<DocumentAnalysis> => {
    const newDocument = await uploadDocumentHook(file, analysisModel);
    addDocument(newDocument);
    return newDocument;
  };

  const toggleDocumentPrivacy = async (id: string): Promise<DocumentAnalysis> => {
    const updatedDoc = await togglePrivacyHook(id);
    updateDocument(id, { isPrivate: updatedDoc.isPrivate });
    return updatedDoc;
  };

  return (
    <DocumentContext.Provider
      value={{
        documents,
        isLoading,
        uploadDocument,
        getDocumentById,
        toggleDocumentPrivacy,
        getStats,
        getCommunityLeads,
        refreshDocuments
      }}
    >
      {children}
    </DocumentContext.Provider>
  );
};

export const useDocuments = (): DocumentContextType => {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error('useDocuments must be used within a DocumentProvider');
  }
  return context;
};
