/**
 * ComplianceStatus Component - Week 4 Implementation
 * Displays Brazilian legal compliance status with CPC Article 889 validation
 */

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { 
  Shield, 
  ShieldCheck, 
  ShieldAlert, 
  ShieldX, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Info,
  Scale
} from 'lucide-react'

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
}

interface ComplianceStatusProps {
  compliance: ComplianceResult
  showDetails?: boolean
  className?: string
}

const getComplianceIcon = (isCompliant: boolean, score: number) => {
  if (isCompliant && score >= 90) return <ShieldCheck className="h-5 w-5 text-green-600" />
  if (isCompliant) return <Shield className="h-5 w-5 text-blue-600" />
  if (score >= 50) return <ShieldAlert className="h-5 w-5 text-yellow-600" />
  return <ShieldX className="h-5 w-5 text-red-600" />
}

const getComplianceColor = (isCompliant: boolean, score: number): string => {
  if (isCompliant && score >= 90) return "text-green-600"
  if (isCompliant) return "text-blue-600"
  if (score >= 50) return "text-yellow-600"
  return "text-red-600"
}

const getComplianceBg = (isCompliant: boolean, score: number): string => {
  if (isCompliant && score >= 90) return "bg-green-50 border-green-200"
  if (isCompliant) return "bg-blue-50 border-blue-200"
  if (score >= 50) return "bg-yellow-50 border-yellow-200"
  return "bg-red-50 border-red-200"
}

const getProgressColor = (score: number): string => {
  if (score >= 90) return "bg-green-500"
  if (score >= 80) return "bg-blue-500"
  if (score >= 50) return "bg-yellow-500"
  return "bg-red-500"
}

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'critical':
      return <XCircle className="h-4 w-4 text-red-500" />
    case 'high':
      return <AlertTriangle className="h-4 w-4 text-orange-500" />
    case 'medium':
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    default:
      return <Info className="h-4 w-4 text-blue-500" />
  }
}

export const ComplianceStatus: React.FC<ComplianceStatusProps> = ({
  compliance,
  showDetails = false,
  className = ""
}) => {
  const complianceIcon = getComplianceIcon(compliance.is_compliant, compliance.compliance_score)
  const complianceColor = getComplianceColor(compliance.is_compliant, compliance.compliance_score)
  const complianceBg = getComplianceBg(compliance.is_compliant, compliance.compliance_score)

  // Calculate CPC 889 compliance stats
  const cpcRequirements = Object.values(compliance.cpc_889_compliance || {})
  const cpcCompliantCount = cpcRequirements.filter(req => req.compliant).length
  const cpcTotalCount = cpcRequirements.length

  // Calculate mandatory requirements stats
  const mandatoryRequirements = Object.values(compliance.mandatory_requirements || {})
  const mandatoryCompliantCount = mandatoryRequirements.filter(Boolean).length
  const mandatoryTotalCount = mandatoryRequirements.length

  return (
    <TooltipProvider>
      <Card className={`${complianceBg} ${className}`}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            {complianceIcon}
            Conformidade Legal
            <Tooltip>
              <TooltipTrigger>
                <Scale className="h-4 w-4 text-gray-400" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Validação automática CPC Art. 889 e requisitos brasileiros</p>
              </TooltipContent>
            </Tooltip>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Overall Compliance Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`text-2xl font-bold ${complianceColor}`}>
                {Math.round(compliance.compliance_score)}%
              </div>
              <div>
                <Badge 
                  variant={compliance.is_compliant ? "default" : "destructive"}
                  className={complianceColor}
                >
                  {compliance.compliance_level}
                </Badge>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-xs text-gray-500">Confiança</div>
              <div className={`text-sm font-medium ${complianceColor}`}>
                {Math.round(compliance.confidence_level * 100)}%
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <Progress 
              value={compliance.compliance_score} 
              className="h-2"
              style={{
                '--progress-background': getProgressColor(compliance.compliance_score)
              } as React.CSSProperties}
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Não Conforme</span>
              <span>Parcial</span>
              <span>Conforme</span>
            </div>
          </div>

          {/* CPC 889 Compliance */}
          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-700">
                CPC Artigo 889
              </div>
              <div className="text-sm">
                <span className={complianceColor}>{cpcCompliantCount}</span>
                <span className="text-gray-500">/{cpcTotalCount}</span>
              </div>
            </div>
            
            {showDetails && (
              <div className="space-y-1">
                {Object.entries(compliance.cpc_889_compliance || {}).map(([key, requirement]) => (
                  <div key={key} className="flex items-center gap-2 text-xs">
                    {requirement.compliant ? (
                      <CheckCircle2 className="h-3 w-3 text-green-500" />
                    ) : (
                      <XCircle className="h-3 w-3 text-red-500" />
                    )}
                    <span className={requirement.compliant ? "text-green-700" : "text-red-700"}>
                      {requirement.description}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Mandatory Requirements */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-700">
                Requisitos Obrigatórios
              </div>
              <div className="text-sm">
                <span className={complianceColor}>{mandatoryCompliantCount}</span>
                <span className="text-gray-500">/{mandatoryTotalCount}</span>
              </div>
            </div>
            
            {mandatoryCompliantCount < mandatoryTotalCount && (
              <div className="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded">
                {mandatoryTotalCount - mandatoryCompliantCount} requisito(s) obrigatório(s) em falta
              </div>
            )}
          </div>

          {/* Violations */}
          {compliance.violations && compliance.violations.length > 0 && (
            <div className="space-y-2 pt-2 border-t">
              <div className="text-sm font-medium text-red-600 flex items-center gap-1">
                <AlertTriangle className="h-4 w-4" />
                Violações ({compliance.violations.length})
              </div>
              <div className="space-y-1">
                {compliance.violations.slice(0, 3).map((violation, index) => (
                  <div key={index} className="flex items-start gap-2 text-xs bg-red-50 px-2 py-1 rounded">
                    {getSeverityIcon(violation.severity)}
                    <span className="text-red-700">{violation.description}</span>
                  </div>
                ))}
                {compliance.violations.length > 3 && (
                  <div className="text-xs text-gray-500">
                    +{compliance.violations.length - 3} outras violações...
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Warnings */}
          {compliance.warnings && compliance.warnings.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-yellow-600 flex items-center gap-1">
                <AlertTriangle className="h-4 w-4" />
                Avisos ({compliance.warnings.length})
              </div>
              <div className="space-y-1">
                {compliance.warnings.slice(0, 2).map((warning, index) => (
                  <div key={index} className="flex items-start gap-2 text-xs bg-yellow-50 px-2 py-1 rounded">
                    <AlertTriangle className="h-3 w-3 text-yellow-500" />
                    <span className="text-yellow-700">{warning.description}</span>
                  </div>
                ))}
                {compliance.warnings.length > 2 && (
                  <div className="text-xs text-gray-500">
                    +{compliance.warnings.length - 2} outros avisos...
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Success Message */}
          {compliance.is_compliant && compliance.compliance_score >= 90 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <div className="flex items-center gap-2 text-sm text-green-700">
                <CheckCircle2 className="h-4 w-4" />
                <span className="font-medium">Totalmente Conforme</span>
              </div>
              <div className="text-xs text-green-600 mt-1">
                Documento atende a todos os requisitos legais brasileiros
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </TooltipProvider>
  )
}

export default ComplianceStatus