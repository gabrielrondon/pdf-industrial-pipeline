
import { DocumentAnalysis, DocumentType, DashboardStats } from '@/types';
import { AIModel } from '@/components/document/ModelSelector';

export interface DocumentContextType {
  documents: DocumentAnalysis[];
  isLoading: boolean;
  uploadDocument: (file: File, analysisModel?: AIModel) => Promise<DocumentAnalysis>;
  getDocumentById: (id: string) => DocumentAnalysis | undefined;
  toggleDocumentPrivacy: (id: string) => Promise<DocumentAnalysis>;
  getStats: () => Promise<DashboardStats>;
  getCommunityLeads: () => Promise<DocumentAnalysis[]>;
  refreshDocuments: () => Promise<void>;
}

export interface UploadDocumentParams {
  file: File;
  analysisModel: AIModel;
  user: any;
  startTime: number;
}

export interface DocumentUploadResult {
  documentId: string;
  analysisResult: any;
  analysisDurationMs: number;
}
