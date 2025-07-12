/**
 * useComplianceCheck Hook - Week 4 Implementation
 * React hook for legal compliance validation API integration
 */

import { useState, useCallback } from 'react'
import { useToast } from '@/components/ui/use-toast'

interface ComplianceResult {
  is_compliant: boolean
  compliance_score: number
  compliance_level: string
  cpc_889_compliance: Record<string, {
    compliant: boolean
    description: string
    severity?: string
  }>
  mandatory_requirements: Record<string, boolean>
  violations: Array<{
    description: string
    severity: string
    category: string
  }>
  warnings: Array<{
    description: string
    severity: string
  }>
  confidence_level: number
  validation_timestamp: string
}

interface ComplianceCheckResult {
  compliance_result: ComplianceResult
  job_id: string
  analysis_summary: {
    total_requirements: number
    met_requirements: number
    critical_violations: number
    warnings_count: number
  }
}

interface UseComplianceCheckReturn {
  isLoading: boolean
  error: string | null
  data: ComplianceCheckResult | null
  checkCompliance: (text: string, jobId?: string, documentType?: string) => Promise<ComplianceCheckResult | null>
  clearError: () => void
}

export const useComplianceCheck = (): UseComplianceCheckReturn => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<ComplianceCheckResult | null>(null)
  const { toast } = useToast()

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const checkCompliance = useCallback(async (
    text: string,
    jobId?: string,
    documentType?: string
  ): Promise<ComplianceCheckResult | null> => {
    if (!text.trim()) {
      setError('Texto é obrigatório para verificação de conformidade')
      return null
    }

    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        throw new Error('Token de autenticação não encontrado')
      }

      const response = await fetch('/api/v1/compliance/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          text,
          job_id: jobId,
          document_type: documentType || 'judicial_auction'
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      
      if (!result.success) {
        throw new Error(result.message || 'Erro na verificação de conformidade')
      }

      const complianceData = result.data as ComplianceCheckResult
      setData(complianceData)

      // Show appropriate toast based on compliance status
      if (complianceData.compliance_result.is_compliant) {
        toast({
          title: "Documento conforme",
          description: `Pontuação: ${Math.round(complianceData.compliance_result.compliance_score)}% - ${complianceData.compliance_result.compliance_level}`,
          duration: 3000
        })
      } else {
        toast({
          title: "Documento não conforme",
          description: `${complianceData.compliance_result.violations.length} violações encontradas`,
          variant: "destructive",
          duration: 5000
        })
      }

      return complianceData
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido na verificação de conformidade'
      setError(errorMessage)
      
      toast({
        title: "Erro na verificação de conformidade",
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
    checkCompliance,
    clearError
  }
}

export default useComplianceCheck