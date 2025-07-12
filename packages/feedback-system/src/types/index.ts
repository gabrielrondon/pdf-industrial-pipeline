import { z } from 'zod';

// Core feedback types
export enum FeedbackType {
  QUICK_QUESTION = 'quick_question',
  DETAILED_INPUT = 'detailed_input',
  MISSING_INFO = 'missing_info',
  PEER_VALIDATION = 'peer_validation',
  QUALITY_RATING = 'quality_rating'
}

export enum DocumentType {
  IPTU = 'iptu',
  PROPERTY_VALUATION = 'property_valuation',
  RISK_ASSESSMENT = 'risk_assessment',
  JUDICIAL_AUCTION = 'judicial_auction',
  LEGAL_DOCUMENT = 'legal_document',
  FINANCIAL_STATEMENT = 'financial_statement'
}

export enum FeedbackQuestionType {
  YES_NO = 'yes_no',
  RATING = 'rating',
  TEXT_INPUT = 'text_input',
  MULTIPLE_CHOICE = 'multiple_choice',
  CURRENCY = 'currency',
  SELECT = 'select'
}

export enum FeedbackStatus {
  PENDING = 'pending',
  SUBMITTED = 'submitted',
  VALIDATED = 'validated',
  REJECTED = 'rejected'
}

// Zod schemas for validation
export const FeedbackQuestionSchema = z.object({
  id: z.string(),
  type: z.nativeEnum(FeedbackQuestionType),
  question: z.string(),
  required: z.boolean().default(false),
  creditReward: z.number().min(0),
  options: z.array(z.string()).optional(), // For multiple choice/select
  placeholder: z.string().optional(),
  helpText: z.string().optional(),
  validation: z.object({
    min: z.number().optional(),
    max: z.number().optional(),
    pattern: z.string().optional()
  }).optional()
});

export const FeedbackAnswerSchema = z.object({
  questionId: z.string(),
  value: z.union([z.string(), z.number(), z.boolean()]),
  confidence: z.number().min(0).max(1).optional(),
  timeSpent: z.number().optional() // seconds
});

export const FeedbackSubmissionSchema = z.object({
  documentId: z.string(),
  documentType: z.nativeEnum(DocumentType),
  feedbackType: z.nativeEnum(FeedbackType),
  answers: z.array(FeedbackAnswerSchema),
  userId: z.string(),
  sessionId: z.string().optional(),
  metadata: z.record(z.any()).optional()
});

export const MissingInfoReportSchema = z.object({
  documentId: z.string(),
  category: z.enum(['financial', 'legal', 'property_details', 'risk_factors', 'other']),
  description: z.string().min(10).max(500),
  specificField: z.string().optional(),
  suggestedValue: z.string().optional(),
  severity: z.enum(['low', 'medium', 'high']).default('medium'),
  userId: z.string()
});

export const CreditRewardSchema = z.object({
  baseCredits: z.number().min(0),
  multiplier: z.number().min(1).default(1),
  bonus: z.number().min(0).default(0),
  reason: z.string(),
  qualityScore: z.number().min(0).max(1).optional()
});

// TypeScript types derived from schemas
export type FeedbackQuestion = z.infer<typeof FeedbackQuestionSchema>;
export type FeedbackAnswer = z.infer<typeof FeedbackAnswerSchema>;
export type FeedbackSubmission = z.infer<typeof FeedbackSubmissionSchema>;
export type MissingInfoReport = z.infer<typeof MissingInfoReportSchema>;
export type CreditReward = z.infer<typeof CreditRewardSchema>;

// Document-specific question templates
export interface DocumentQuestionTemplate {
  documentType: DocumentType;
  questions: FeedbackQuestion[];
  triggerConditions?: {
    confidenceThreshold?: number;
    missingFields?: string[];
    userPlan?: string[];
  };
}

// User feedback history and statistics
export interface UserFeedbackStats {
  userId: string;
  totalSubmissions: number;
  creditsEarned: number;
  averageQuality: number;
  streakDays: number;
  badges: string[];
  multiplierTier: number;
  lastSubmission: Date;
}

// Peer validation
export interface PeerValidationTask {
  id: string;
  originalDocumentId: string;
  originalUserId: string;
  validatorUserId: string;
  feedbackToValidate: FeedbackSubmission;
  validationResult: 'agree' | 'disagree' | 'partial';
  validationNotes?: string;
  creditReward: number;
  completedAt?: Date;
}

// Real-time feedback state
export interface FeedbackSession {
  sessionId: string;
  documentId: string;
  userId: string;
  startedAt: Date;
  currentQuestionIndex: number;
  answers: FeedbackAnswer[];
  timeSpentPerQuestion: number[];
  isComplete: boolean;
  creditsEarned: number;
}

// API response types
export interface FeedbackApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  credits?: CreditReward;
}

export interface DocumentFeedbackContext {
  documentId: string;
  documentType: DocumentType;
  mlPredictions?: Record<string, any>;
  userPlan: string;
  existingFeedback?: FeedbackSubmission[];
}

// Configuration for easy removal
export interface FeedbackSystemConfig {
  enabled: boolean;
  apiEndpoint: string;
  creditMultipliers: Record<string, number>;
  maxQuestionsPerSession: number;
  cooldownBetweenSessions: number; // minutes
  peerValidationEnabled: boolean;
  gamificationEnabled: boolean;
}