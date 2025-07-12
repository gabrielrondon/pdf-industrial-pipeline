/**
 * RecommendationsList Component - Week 4 Implementation
 * Displays prioritized, actionable recommendations for document improvement
 */

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { 
  Lightbulb, 
  AlertTriangle, 
  TrendingUp, 
  Clock, 
  Target,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  Zap,
  Calendar,
  Info
} from 'lucide-react'

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
}

interface RecommendationsListProps {
  recommendations: RecommendationSet
  onRecommendationComplete?: (recommendationId: string) => void
  className?: string
}

const getPriorityColor = (priority: string): string => {
  switch (priority) {
    case 'critical': return 'text-red-600 bg-red-50 border-red-200'
    case 'high': return 'text-orange-600 bg-orange-50 border-orange-200'
    case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'low': return 'text-gray-600 bg-gray-50 border-gray-200'
    default: return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

const getPriorityIcon = (priority: string) => {
  switch (priority) {
    case 'critical': return <AlertTriangle className="h-4 w-4 text-red-500" />
    case 'high': return <TrendingUp className="h-4 w-4 text-orange-500" />
    case 'medium': return <Target className="h-4 w-4 text-yellow-500" />
    case 'low': return <Info className="h-4 w-4 text-gray-500" />
    default: return <Info className="h-4 w-4 text-gray-500" />
  }
}

const getImpactEffortBadge = (impact: string, effort: string) => {
  const isQuickWin = impact === 'high' && effort === 'low'
  if (isQuickWin) {
    return (
      <Badge variant="default" className="bg-green-100 text-green-700 border-green-300">
        <Zap className="h-3 w-3 mr-1" />
        Quick Win
      </Badge>
    )
  }
  
  return (
    <div className="flex gap-1">
      <Badge variant="outline" className="text-xs">
        Impacto: {impact === 'high' ? 'Alto' : impact === 'medium' ? 'Médio' : 'Baixo'}
      </Badge>
      <Badge variant="outline" className="text-xs">
        Esforço: {effort === 'low' ? 'Baixo' : effort === 'medium' ? 'Médio' : 'Alto'}
      </Badge>
    </div>
  )
}

const RecommendationCard: React.FC<{
  recommendation: Recommendation
  onComplete?: (id: string) => void
}> = ({ recommendation, onComplete }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  
  const priorityColor = getPriorityColor(recommendation.priority)
  const priorityIcon = getPriorityIcon(recommendation.priority)

  const handleComplete = () => {
    setIsCompleted(true)
    onComplete?.(recommendation.id)
  }

  return (
    <Card className={`${priorityColor} ${isCompleted ? 'opacity-60' : ''}`}>
      <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-opacity-80 transition-colors pb-3">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                {priorityIcon}
                <div className="flex-1">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    {recommendation.title}
                    {recommendation.affects_compliance && (
                      <Badge variant="outline" className="text-xs">
                        Legal
                      </Badge>
                    )}
                    {isCompleted && (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    )}
                  </CardTitle>
                  <p className="text-xs text-gray-600 mt-1">
                    {recommendation.description}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {getImpactEffortBadge(recommendation.impact, recommendation.effort)}
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                )}
              </div>
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        
        <CollapsibleContent>
          <CardContent className="pt-0 space-y-3">
            <div className="bg-white bg-opacity-50 rounded-lg p-3 space-y-2">
              <div>
                <span className="text-xs font-medium text-gray-700">Ação específica:</span>
                <p className="text-sm text-gray-800 mt-1">
                  {recommendation.specific_action}
                </p>
              </div>
              
              {recommendation.example && (
                <div>
                  <span className="text-xs font-medium text-gray-700">Exemplo:</span>
                  <p className="text-sm text-gray-600 italic mt-1">
                    "{recommendation.example}"
                  </p>
                </div>
              )}
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>Categoria: {recommendation.category}</span>
                <span>•</span>
                <span>Tipo: {recommendation.action_type}</span>
              </div>
              
              <Button 
                size="sm" 
                variant={isCompleted ? "outline" : "default"}
                onClick={handleComplete}
                disabled={isCompleted}
                className="text-xs"
              >
                {isCompleted ? (
                  <>
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Concluído
                  </>
                ) : (
                  'Marcar como Feito'
                )}
              </Button>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}

export const RecommendationsList: React.FC<RecommendationsListProps> = ({
  recommendations,
  onRecommendationComplete,
  className = ""
}) => {
  const allRecommendations = [
    ...recommendations.critical_recommendations,
    ...recommendations.high_priority_recommendations,
    ...recommendations.medium_priority_recommendations
  ]

  return (
    <TooltipProvider>
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-blue-600" />
            Recomendações Inteligentes
            <Badge variant="secondary">
              {recommendations.total_recommendations}
            </Badge>
          </CardTitle>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <TrendingUp className="h-4 w-4" />
              Melhoria estimada: +{Math.round(recommendations.estimated_improvement)} pontos
            </div>
            <div className="flex items-center gap-1">
              <Zap className="h-4 w-4" />
              {recommendations.quick_wins.length} quick wins
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <Tabs defaultValue="priority" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="priority">Por Prioridade</TabsTrigger>
              <TabsTrigger value="quickwins">Quick Wins</TabsTrigger>
              <TabsTrigger value="timeline">Cronograma</TabsTrigger>
            </TabsList>
            
            <TabsContent value="priority" className="space-y-4">
              {recommendations.critical_recommendations.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-red-600">
                    <AlertTriangle className="h-4 w-4" />
                    Críticas ({recommendations.critical_recommendations.length})
                  </div>
                  {recommendations.critical_recommendations.map((rec) => (
                    <RecommendationCard
                      key={rec.id}
                      recommendation={rec}
                      onComplete={onRecommendationComplete}
                    />
                  ))}
                </div>
              )}
              
              {recommendations.high_priority_recommendations.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-orange-600">
                    <TrendingUp className="h-4 w-4" />
                    Alta Prioridade ({recommendations.high_priority_recommendations.length})
                  </div>
                  {recommendations.high_priority_recommendations.map((rec) => (
                    <RecommendationCard
                      key={rec.id}
                      recommendation={rec}
                      onComplete={onRecommendationComplete}
                    />
                  ))}
                </div>
              )}
              
              {recommendations.medium_priority_recommendations.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-yellow-600">
                    <Target className="h-4 w-4" />
                    Média Prioridade ({recommendations.medium_priority_recommendations.length})
                  </div>
                  {recommendations.medium_priority_recommendations.map((rec) => (
                    <RecommendationCard
                      key={rec.id}
                      recommendation={rec}
                      onComplete={onRecommendationComplete}
                    />
                  ))}
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="quickwins" className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-green-700 font-medium mb-2">
                  <Zap className="h-5 w-5" />
                  Quick Wins - Alto Impacto, Baixo Esforço
                </div>
                <p className="text-sm text-green-600 mb-3">
                  Essas ações oferecem o melhor retorno sobre investimento de tempo.
                </p>
              </div>
              
              {recommendations.quick_wins.length > 0 ? (
                <div className="space-y-2">
                  {recommendations.quick_wins.map((rec) => (
                    <RecommendationCard
                      key={rec.id}
                      recommendation={rec}
                      onComplete={onRecommendationComplete}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Zap className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>Nenhum quick win identificado neste momento</p>
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="timeline" className="space-y-4">
              <div className="space-y-4">
                {/* Immediate Actions */}
                {recommendations.action_plan.immediate_actions.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium text-red-600">
                      <AlertTriangle className="h-4 w-4" />
                      Ações Imediatas
                    </div>
                    <div className="space-y-1">
                      {recommendations.action_plan.immediate_actions.map((action, index) => (
                        <div key={index} className="bg-red-50 border border-red-200 rounded p-2 text-sm">
                          {action}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Short-term Actions */}
                {recommendations.action_plan.short_term_actions.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium text-orange-600">
                      <Clock className="h-4 w-4" />
                      Curto Prazo (1-2 semanas)
                    </div>
                    <div className="space-y-1">
                      {recommendations.action_plan.short_term_actions.map((action, index) => (
                        <div key={index} className="bg-orange-50 border border-orange-200 rounded p-2 text-sm">
                          {action}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Long-term Actions */}
                {recommendations.action_plan.long_term_actions.length > 0 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium text-blue-600">
                      <Calendar className="h-4 w-4" />
                      Longo Prazo (1+ mês)
                    </div>
                    <div className="space-y-1">
                      {recommendations.action_plan.long_term_actions.map((action, index) => (
                        <div key={index} className="bg-blue-50 border border-blue-200 rounded p-2 text-sm">
                          {action}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </TooltipProvider>
  )
}

export default RecommendationsList