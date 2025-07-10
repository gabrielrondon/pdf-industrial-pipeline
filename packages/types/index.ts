// Shared types across the monorepo

export interface DocumentInfo {
  id: string
  filename: string
  size: number
  uploadedAt: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  analysisType: 'native' | 'ai'
}

export interface ProcessingJob {
  id: string
  documentId: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  startedAt?: string
  completedAt?: string
  error?: string
}

export interface AnalysisResult {
  jobId: string
  documentId: string
  analysisType: 'native' | 'ai'
  result: any
  confidence?: number
  processingTime: number
  extractedData?: {
    leadScore?: number
    riskFactors?: string[]
    opportunities?: string[]
    summary?: string
  }
}

export interface User {
  id: string
  email: string
  name: string
  role: 'user' | 'admin'
  plan: 'free' | 'pro' | 'premium'
  credits: number
  createdAt: string
}

export interface SystemStats {
  totalDocuments: number
  activeJobs: number
  totalUsers: number
  systemUptime: string
  dbConnections: number
  apiStatus: 'healthy' | 'warning' | 'error'
  lastUpdate: string
}

export interface MLModel {
  name: string
  version: string
  status: 'active' | 'training' | 'idle' | 'error'
  accuracy?: number
  lastTrained?: string
  size: string
  description?: string
}

export interface DatabaseConfig {
  host: string
  port: number
  database: string
  username: string
  password: string
  ssl: boolean
  poolSize?: number
}