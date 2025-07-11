
export type UserPlan = 'free' | 'pro' | 'premium';

export interface User {
  id: string;
  email: string;
  name?: string;
  plan: UserPlan;
  credits: number;
  credits_used: number;
  credits_earned: number;
  createdAt: string;
}

export interface PlanFeature {
  title: string;
  free: boolean;
  pro: boolean;
  premium: boolean;
}

export interface PlanDetails {
  id: UserPlan;
  name: string;
  price: number;
  description: string;
  features: PlanFeature[];
  color: string;
  recommended?: boolean;
  credits: number;
}

export type DocumentType = 'edital' | 'processo' | 'laudo' | 'outro';

export type AnalysisStatus = 'confirmado' | 'alerta' | 'não identificado';

export interface AnalysisPoint {
  id: string;
  title: string;
  status: AnalysisStatus;
  comment: string;
}

export interface DocumentAnalysis {
  id: string;
  userId: string;
  fileName: string;
  fileUrl: string;
  type: DocumentType;
  uploadedAt: string;
  analyzedAt: string;
  isPrivate: boolean;
  points: AnalysisPoint[];
}

export interface DashboardStats {
  totalAnalyses: number;
  validLeads: number;
  sharedLeads: number;
  credits: number;
  documentTypes: { type: DocumentType; count: number }[];
  statusDistribution: { status: AnalysisStatus; count: number }[];
  commonIssues: { issue: string; count: number }[];
  // Novas métricas para estatísticas mais ricas
  monthlyAnalyses?: { month: string; analyses: number; leads: number }[];
  successRate?: number;
  averageProcessingTime?: number;
  totalFileSize?: number;
  averageConfidence?: number;
  topPerformingDocumentType?: DocumentType;
}

export interface CreditTransaction {
  id: string;
  user_id: string;
  type: 'earned' | 'spent' | 'granted' | 'plan_upgrade';
  amount: number;
  reason: string;
  document_id?: string;
  created_at: string;
}
