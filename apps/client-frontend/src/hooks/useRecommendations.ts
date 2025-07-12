/**
 * useRecommendations Hook - Week 4 Implementation
 * React hook for intelligent recommendations API integration
 */

import { useState, useCallback } from 'react'
import { useToast } from '@/components/ui/use-toast'

interface Recommendation {
  id: string
  title: string
  description: string
  category: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  impact: 'high' | 'medium' | 'low'
  effort: 'low' | 'medium' | 'high'
  action_type: string
  specific_action: string
  example?: string
  affects_compliance: boolean
}

interface RecommendationSet {
  total_recommendations: number
  estimated_improvement: number
  critical_recommendations: Recommendation[]
  high_priority_recommendations: Recommendation[]
  medium_priority_recommendations: Recommendation[]
  quick_wins: Recommendation[]
  action_plan: {
    immediate_actions: string[]
    short_term_actions: string[]
    long_term_actions: string[]
  }
  generation_timestamp: string
}

interface RecommendationsResult {
  recommendations: RecommendationSet
  job_id: string
  analysis_context: {
    quality_score: number
    compliance_score: number
    main_issues: string[]
    improvement_areas: string[]
  }
}

interface UseRecommendationsReturn {
  isLoading: boolean
  error: string | null
  data: RecommendationsResult | null
  generateRecommendations: (text: string, jobId?: string, qualityMetrics?: any, complianceResult?: any) => Promise<RecommendationsResult | null>
  markRecommendationComplete: (recommendationId: string) => Promise<boolean>
  clearError: () => void
}

export const useRecommendations = (): UseRecommendationsReturn => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<RecommendationsResult | null>(null)
  const { toast } = useToast()

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const generateRecommendations = useCallback(async (
    text: string,
    jobId?: string,
    qualityMetrics?: any,
    complianceResult?: any
  ): Promise<RecommendationsResult | null> => {
    if (!text.trim()) {
      setError('Texto é obrigatório para geração de recomendações')
      return null
    }

    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error('Token de autenticação não encontrado')
      }

      const response = await fetch('/api/v1/recommendations/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          text,
          job_id: jobId,
          quality_metrics: qualityMetrics,
          compliance_result: complianceResult,
          context: {
            document_type: 'judicial_auction',
            language: 'pt-BR'
          }
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      
      if (!result.success) {
        throw new Error(result.message || 'Erro na geração de recomendações')
      }

      const recommendationsData = result.data as RecommendationsResult
      setData(recommendationsData)

      // Show success toast with summary
      const quickWinsCount = recommendationsData.recommendations.quick_wins.length
      const criticalCount = recommendationsData.recommendations.critical_recommendations.length
      
      toast({
        title: "Recomendações geradas",
        description: `${recommendationsData.recommendations.total_recommendations} recomendações (${quickWinsCount} quick wins, ${criticalCount} críticas)`,
        duration: 3000
      })

      return recommendationsData
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido na geração de recomendações'
      setError(errorMessage)
      
      toast({
        title: "Erro na geração de recomendações",
        description: errorMessage,
        variant: "destructive",
        duration: 5000
      })
      
      return null
    } finally {
      setIsLoading(false)
    }
  }, [toast])

  const markRecommendationComplete = useCallback(async (
    recommendationId: string
  ): Promise<boolean> => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error('Token de autenticação não encontrado')
      }

      const response = await fetch(`/api/v1/recommendations/${recommendationId}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      
      if (!result.success) {
        throw new Error(result.message || 'Erro ao marcar recomendação como concluída')
      }

      toast({
        title: "Recomendação concluída",
        description: "Progresso salvo com sucesso",
        duration: 2000
      })

      return true
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao marcar recomendação'
      
      toast({
        title: "Erro ao marcar recomendação",
        description: errorMessage,
        variant: "destructive",
        duration: 3000
      })
      
      return false
    }
  }, [toast])

  return {
    isLoading,
    error,
    data,
    generateRecommendations,
    markRecommendationComplete,
    clearError
  }
}

export default useRecommendations