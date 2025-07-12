/**
 * useQualityAssessment Hook - Week 4 Implementation
 * React hook for quality assessment API integration
 */

import { useState, useCallback } from 'react'
import { useToast } from '@/components/ui/use-toast'

interface QualityMetrics {
  overall_score: number
  quality_level: string
  completeness_score: number
  compliance_score: number
  clarity_score: number
  information_score: number
  missing_elements: string[]
  compliance_issues: string[]
  quality_indicators: Record<string, any>
  improvement_potential: number
  confidence_level: number
  assessment_timestamp: string
}

interface QualityInsights {
  strengths: string[]
  weaknesses: string[]
  priority_actions: string[]
  improvement_suggestions: string[]
}

interface QualityAssessmentResult {
  quality_metrics: QualityMetrics
  insights: QualityInsights
  job_id: string
}

interface UseQualityAssessmentReturn {
  isLoading: boolean
  error: string | null
  data: QualityAssessmentResult | null
  assessQuality: (text: string, jobId?: string, enhancedFeatures?: any) => Promise<QualityAssessmentResult | null>
  clearError: () => void
}

export const useQualityAssessment = (): UseQualityAssessmentReturn => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<QualityAssessmentResult | null>(null)
  const { toast } = useToast()

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const assessQuality = useCallback(async (
    text: string,
    jobId?: string,
    enhancedFeatures?: any
  ): Promise<QualityAssessmentResult | null> => {
    if (!text.trim()) {
      setError('Texto é obrigatório para avaliação de qualidade')
      return null
    }

    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error('Token de autenticação não encontrado')
      }

      const response = await fetch('/api/v1/quality/assess', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          text,
          job_id: jobId,
          enhanced_features: enhancedFeatures
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      
      if (!result.success) {
        throw new Error(result.message || 'Erro na avaliação de qualidade')
      }

      const assessmentData = result.data as QualityAssessmentResult
      setData(assessmentData)

      // Show success toast
      toast({
        title: "Avaliação de qualidade concluída",
        description: `Pontuação: ${Math.round(assessmentData.quality_metrics.overall_score)}/100 (${assessmentData.quality_metrics.quality_level})`,
        duration: 3000
      })

      return assessmentData
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido na avaliação de qualidade'
      setError(errorMessage)
      
      toast({
        title: "Erro na avaliação de qualidade",
        description: errorMessage,
        variant: "destructive",
        duration: 5000
      })
      
      return null
    } finally {
      setIsLoading(false)
    }
  }, [toast])

  return {
    isLoading,
    error,
    data,
    assessQuality,
    clearError
  }
}

export default useQualityAssessment