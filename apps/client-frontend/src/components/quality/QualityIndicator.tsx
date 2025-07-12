/**
 * QualityIndicator Component - Week 4 Implementation
 * Displays quality score with visual indicators and breakdown
 */

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { AlertCircle, CheckCircle, Info, TrendingUp } from 'lucide-react'

interface QualityMetrics {
  overall_score: number
  quality_level: string
  completeness_score: number
  compliance_score: number
  clarity_score: number
  information_score: number
  confidence_level: number
  improvement_potential: number
  missing_elements: string[]
}

interface QualityIndicatorProps {
  metrics: QualityMetrics
  showDetails?: boolean
  className?: string
}

const getQualityColor = (score: number): string => {
  if (score >= 85) return "text-green-600"
  if (score >= 70) return "text-blue-600"
  if (score >= 50) return "text-yellow-600"
  return "text-red-600"
}

const getQualityBgColor = (score: number): string => {
  if (score >= 85) return "bg-green-50 border-green-200"
  if (score >= 70) return "bg-blue-50 border-blue-200"
  if (score >= 50) return "bg-yellow-50 border-yellow-200"
  return "bg-red-50 border-red-200"
}

const getQualityIcon = (score: number) => {
  if (score >= 85) return <CheckCircle className="h-5 w-5 text-green-600" />
  if (score >= 70) return <Info className="h-5 w-5 text-blue-600" />
  if (score >= 50) return <AlertCircle className="h-5 w-5 text-yellow-600" />
  return <AlertCircle className="h-5 w-5 text-red-600" />
}

const getProgressColor = (score: number): string => {
  if (score >= 85) return "bg-green-500"
  if (score >= 70) return "bg-blue-500"
  if (score >= 50) return "bg-yellow-500"
  return "bg-red-500"
}

export const QualityIndicator: React.FC<QualityIndicatorProps> = ({
  metrics,
  showDetails = false,
  className = ""
}) => {
  const qualityColor = getQualityColor(metrics.overall_score)
  const qualityBg = getQualityBgColor(metrics.overall_score)
  const qualityIcon = getQualityIcon(metrics.overall_score)

  const componentScores = [
    { name: 'Completude', score: metrics.completeness_score, description: 'Informações essenciais presentes' },
    { name: 'Conformidade', score: metrics.compliance_score, description: 'Conformidade legal (CPC Art. 889)' },
    { name: 'Clareza', score: metrics.clarity_score, description: 'Estrutura e legibilidade do texto' },
    { name: 'Informação', score: metrics.information_score, description: 'Densidade e utilidade das informações' }
  ]

  return (
    <TooltipProvider>
      <Card className={`${qualityBg} ${className}`}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            {qualityIcon}
            Qualidade do Documento
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-4 w-4 text-gray-400" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Avaliação automática baseada em 50+ critérios</p>
              </TooltipContent>
            </Tooltip>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Overall Score */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`text-3xl font-bold ${qualityColor}`}>
                {Math.round(metrics.overall_score)}
              </div>
              <div>
                <div className="text-sm font-medium">/ 100</div>
                <Badge variant="secondary" className={qualityColor}>
                  {metrics.quality_level}
                </Badge>
              </div>
            </div>
            
            {metrics.improvement_potential > 0 && (
              <div className="text-right">
                <div className="text-xs text-gray-500">Potencial de melhoria</div>
                <div className="flex items-center gap-1 text-sm text-green-600">
                  <TrendingUp className="h-3 w-3" />
                  +{Math.round(metrics.improvement_potential)} pontos
                </div>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="relative">
              <Progress 
                value={metrics.overall_score} 
                className="h-2"
                style={{
                  '--progress-background': getProgressColor(metrics.overall_score)
                } as React.CSSProperties}
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>50</span>
                <span>100</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2 text-xs">
              <span className="text-gray-500">Confiança:</span>
              <span className={qualityColor}>
                {Math.round(metrics.confidence_level * 100)}%
              </span>
            </div>
          </div>

          {/* Component Breakdown */}
          {showDetails && (
            <div className="space-y-3 pt-2 border-t">
              <div className="text-sm font-medium text-gray-700">
                Breakdown por Componente
              </div>
              
              {componentScores.map((component) => (
                <div key={component.name} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <Tooltip>
                      <TooltipTrigger className="flex items-center gap-1">
                        <span>{component.name}</span>
                        <Info className="h-3 w-3 text-gray-400" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{component.description}</p>
                      </TooltipContent>
                    </Tooltip>
                    <span className={getQualityColor(component.score)}>
                      {Math.round(component.score)}%
                    </span>
                  </div>
                  <Progress 
                    value={component.score} 
                    className="h-1"
                    style={{
                      '--progress-background': getProgressColor(component.score)
                    } as React.CSSProperties}
                  />
                </div>
              ))}
            </div>
          )}

          {/* Missing Elements Alert */}
          {metrics.missing_elements && metrics.missing_elements.length > 0 && (
            <div className="space-y-2 pt-2 border-t">
              <div className="text-sm font-medium text-orange-600 flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                Elementos em Falta ({metrics.missing_elements.length})
              </div>
              <div className="space-y-1">
                {metrics.missing_elements.slice(0, 3).map((element, index) => (
                  <div key={index} className="text-xs text-gray-600 bg-orange-50 px-2 py-1 rounded">
                    • {element}
                  </div>
                ))}
                {metrics.missing_elements.length > 3 && (
                  <div className="text-xs text-gray-500">
                    +{metrics.missing_elements.length - 3} outros...
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </TooltipProvider>
  )
}

export default QualityIndicator