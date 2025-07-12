"""
Recommendation Engine - Week 3 Implementation
Intelligent recommendation system for Brazilian judicial auction document improvements
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from .quality_assessor import QualityMetrics
from .compliance_checker import ComplianceResult

logger = logging.getLogger(__name__)

@dataclass
class Recommendation:
    """Individual recommendation for document improvement"""
    
    id: str
    title: str
    description: str
    category: str  # quality, compliance, legal, information
    priority: str  # critical, high, medium, low
    impact: str   # high, medium, low
    effort: str   # low, medium, high
    
    # Action details
    action_type: str  # add, fix, improve, verify
    specific_action: str
    example: Optional[str] = None
    
    # Context
    related_score: float = 0.0
    affects_compliance: bool = False
    
    # Metadata
    created_at: str = ""

@dataclass
class RecommendationSet:
    """Complete set of recommendations for a document"""
    
    # Recommendations by priority
    critical_recommendations: List[Recommendation] = None
    high_priority_recommendations: List[Recommendation] = None
    medium_priority_recommendations: List[Recommendation] = None
    low_priority_recommendations: List[Recommendation] = None
    
    # Summary
    total_recommendations: int = 0
    estimated_improvement: float = 0.0  # Expected score improvement
    
    # Quick wins (high impact, low effort)
    quick_wins: List[Recommendation] = None
    
    # Action plan
    immediate_actions: List[str] = None
    short_term_actions: List[str] = None
    long_term_actions: List[str] = None
    
    # Metadata
    generated_at: str = ""
    
    def __post_init__(self):
        if self.critical_recommendations is None:
            self.critical_recommendations = []
        if self.high_priority_recommendations is None:
            self.high_priority_recommendations = []
        if self.medium_priority_recommendations is None:
            self.medium_priority_recommendations = []
        if self.low_priority_recommendations is None:
            self.low_priority_recommendations = []
        if self.quick_wins is None:
            self.quick_wins = []
        if self.immediate_actions is None:
            self.immediate_actions = []
        if self.short_term_actions is None:
            self.short_term_actions = []
        if self.long_term_actions is None:
            self.long_term_actions = []

class RecommendationEngine:
    """
    Intelligent recommendation engine for Brazilian judicial auction documents
    Generates actionable, prioritized recommendations based on quality and compliance analysis
    """
    
    def __init__(self):
        """Initialize recommendation engine"""
        self.recommendation_templates = self._build_recommendation_templates()
        self.improvement_strategies = self._build_improvement_strategies()
        self.priority_matrix = self._build_priority_matrix()
        
        logger.info("Recommendation Engine initialized")
    
    def _build_recommendation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Build templates for common recommendations"""
        return {
            # Quality improvement templates
            'add_process_number': {
                'title': 'Adicionar número do processo',
                'description': 'Incluir o número completo do processo judicial no formato CNJ',
                'category': 'compliance',
                'action_type': 'add',
                'specific_action': 'Inserir número do processo no formato: 1234567-89.2023.8.26.0100',
                'example': 'Processo nº 1234567-89.2023.8.26.0100',
                'priority': 'critical',
                'impact': 'high',
                'effort': 'low'
            },
            'add_cpc_reference': {
                'title': 'Incluir referência ao CPC',
                'description': 'Adicionar referência expressa ao art. 889 do Código de Processo Civil',
                'category': 'compliance',
                'action_type': 'add',
                'specific_action': 'Incluir texto: "nos termos do art. 889 do CPC"',
                'example': 'Nos termos do art. 889 do Código de Processo Civil, será realizada hasta pública...',
                'priority': 'critical',
                'impact': 'high',
                'effort': 'low'
            },
            'add_property_address': {
                'title': 'Completar endereço do imóvel',
                'description': 'Incluir endereço completo com rua, número, bairro, cidade e CEP',
                'category': 'information',
                'action_type': 'add',
                'specific_action': 'Adicionar endereço completo do imóvel',
                'example': 'Rua das Flores, 123, Bairro Jardim, São Paulo/SP, CEP 01234-567',
                'priority': 'high',
                'impact': 'high',
                'effort': 'medium'
            },
            'add_valuation': {
                'title': 'Informar valor da avaliação',
                'description': 'Incluir o valor da avaliação do imóvel em moeda corrente',
                'category': 'compliance',
                'action_type': 'add',
                'specific_action': 'Especificar valor da avaliação em R$',
                'example': 'Valor da avaliação: R$ 450.000,00 (quatrocentos e cinquenta mil reais)',
                'priority': 'critical',
                'impact': 'high',
                'effort': 'low'
            },
            'add_minimum_bid': {
                'title': 'Especificar lance mínimo',
                'description': 'Definir claramente o lance mínimo para participação no leilão',
                'category': 'compliance',
                'action_type': 'add',
                'specific_action': 'Informar lance mínimo (geralmente 2/3 da avaliação)',
                'example': 'Lance mínimo: R$ 300.000,00 (dois terços do valor da avaliação)',
                'priority': 'critical',
                'impact': 'high',
                'effort': 'low'
            },
            'add_auction_date': {
                'title': 'Informar data do leilão',
                'description': 'Especificar data, horário e local do leilão',
                'category': 'compliance',
                'action_type': 'add',
                'specific_action': 'Incluir data, hora e local do leilão',
                'example': 'Data: 15/03/2024, às 14h00, no Fórum Central - Sala de Leilões',
                'priority': 'high',
                'impact': 'high',
                'effort': 'low'
            },
            'add_qualification_deadline': {
                'title': 'Estabelecer prazo de habilitação',
                'description': 'Definir prazo para habilitação de interessados',
                'category': 'compliance',
                'action_type': 'add',
                'specific_action': 'Estabelecer prazo mínimo de 10 dias para habilitação',
                'example': 'Prazo para habilitação: até 10 dias antes da data do leilão',
                'priority': 'high',
                'impact': 'medium',
                'effort': 'low'
            },
            'improve_text_clarity': {
                'title': 'Melhorar clareza do texto',
                'description': 'Revisar texto para maior clareza e estruturação',
                'category': 'quality',
                'action_type': 'improve',
                'specific_action': 'Reorganizar texto em parágrafos claros e usar linguagem jurídica adequada',
                'example': 'Usar frases mais curtas e estruturação em tópicos',
                'priority': 'medium',
                'impact': 'medium',
                'effort': 'medium'
            },
            'add_property_details': {
                'title': 'Detalhar características do imóvel',
                'description': 'Incluir mais detalhes sobre o imóvel (área, quartos, etc.)',
                'category': 'information',
                'action_type': 'add',
                'specific_action': 'Adicionar características físicas do imóvel',
                'example': 'Apartamento com 85m², 3 dormitórios, 2 banheiros, 1 vaga de garagem',
                'priority': 'medium',
                'impact': 'medium',
                'effort': 'medium'
            },
            'add_debt_information': {
                'title': 'Informar valor do débito',
                'description': 'Incluir informações sobre o débito executado',
                'category': 'information',
                'action_type': 'add',
                'specific_action': 'Especificar valor total do débito em execução',
                'example': 'Débito total: R$ 127.000,00 (cento e vinte e sete mil reais)',
                'priority': 'medium',
                'impact': 'low',
                'effort': 'low'
            },
            'add_property_status': {
                'title': 'Informar situação do imóvel',
                'description': 'Esclarecer se o imóvel está ocupado ou livre',
                'category': 'information',
                'action_type': 'add',
                'specific_action': 'Informar situação atual de ocupação',
                'example': 'Situação: imóvel livre de ocupação / ocupado por inquilino',
                'priority': 'medium',
                'impact': 'medium',
                'effort': 'low'
            }
        }
    
    def _build_improvement_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Build improvement strategies for different scenarios"""
        return {
            'low_completeness': {
                'focus': 'Add missing essential information',
                'strategies': [
                    'Identify and add all mandatory elements',
                    'Complete property description',
                    'Add all required financial information',
                    'Include all procedural details'
                ]
            },
            'low_compliance': {
                'focus': 'Fix legal compliance issues',
                'strategies': [
                    'Add CPC Article 889 references',
                    'Include all mandatory legal requirements',
                    'Fix procedural compliance issues',
                    'Add proper legal language'
                ]
            },
            'low_clarity': {
                'focus': 'Improve text structure and readability',
                'strategies': [
                    'Reorganize text into clear sections',
                    'Use proper legal terminology',
                    'Improve sentence structure',
                    'Add clear headings and formatting'
                ]
            },
            'low_information': {
                'focus': 'Increase information density',
                'strategies': [
                    'Add detailed property characteristics',
                    'Include financial details',
                    'Add contact information',
                    'Provide additional relevant details'
                ]
            }
        }
    
    def _build_priority_matrix(self) -> Dict[str, Dict[str, str]]:
        """Build priority matrix based on impact and effort"""
        return {
            'high_impact_low_effort': 'critical',    # Quick wins
            'high_impact_medium_effort': 'high',     # Important improvements
            'high_impact_high_effort': 'high',       # Strategic improvements
            'medium_impact_low_effort': 'medium',    # Easy improvements
            'medium_impact_medium_effort': 'medium', # Balanced improvements
            'medium_impact_high_effort': 'low',      # Consider if worth it
            'low_impact_low_effort': 'low',          # Nice to have
            'low_impact_medium_effort': 'low',       # Low priority
            'low_impact_high_effort': 'low'          # Usually not worth it
        }
    
    def generate_recommendations(self, 
                               quality_metrics: QualityMetrics,
                               compliance_result: ComplianceResult,
                               text: str = "",
                               job_id: str = "") -> RecommendationSet:
        """
        Generate comprehensive recommendations based on quality and compliance analysis
        
        Args:
            quality_metrics: Quality assessment results
            compliance_result: Compliance check results
            text: Original document text (for context)
            job_id: Job identifier for tracking
            
        Returns:
            RecommendationSet with prioritized recommendations
        """
        try:
            recommendation_set = RecommendationSet(
                generated_at=datetime.now().isoformat()
            )
            
            all_recommendations = []
            
            # 1. Generate compliance-based recommendations
            compliance_recs = self._generate_compliance_recommendations(compliance_result)
            all_recommendations.extend(compliance_recs)
            
            # 2. Generate quality-based recommendations
            quality_recs = self._generate_quality_recommendations(quality_metrics)
            all_recommendations.extend(quality_recs)
            
            # 3. Generate contextual recommendations
            contextual_recs = self._generate_contextual_recommendations(quality_metrics, compliance_result, text)
            all_recommendations.extend(contextual_recs)
            
            # 4. Prioritize and organize recommendations
            self._prioritize_recommendations(all_recommendations, recommendation_set)
            
            # 5. Identify quick wins
            recommendation_set.quick_wins = self._identify_quick_wins(all_recommendations)
            
            # 6. Create action plan
            self._create_action_plan(recommendation_set)
            
            # 7. Calculate estimated improvement
            recommendation_set.estimated_improvement = self._calculate_estimated_improvement(
                recommendation_set, quality_metrics.overall_score
            )
            
            recommendation_set.total_recommendations = len(all_recommendations)
            
            logger.info(f"Generated {len(all_recommendations)} recommendations for {job_id}")
            
            return recommendation_set
            
        except Exception as e:
            logger.error(f"Error generating recommendations for {job_id}: {e}")
            return RecommendationSet(
                generated_at=datetime.now().isoformat(),
                total_recommendations=0
            )
    
    def _generate_compliance_recommendations(self, compliance_result: ComplianceResult) -> List[Recommendation]:
        """Generate recommendations based on compliance analysis"""
        
        recommendations = []
        
        # CPC 889 compliance recommendations
        for req_name, req_details in compliance_result.cpc_889_compliance.items():
            if not req_details.get('compliant', False):
                template_key = self._map_requirement_to_template(req_name)
                if template_key and template_key in self.recommendation_templates:
                    template = self.recommendation_templates[template_key]
                    
                    rec = Recommendation(
                        id=f"cpc_{req_name}",
                        title=template['title'],
                        description=template['description'],
                        category=template['category'],
                        priority=template['priority'],
                        impact=template['impact'],
                        effort=template['effort'],
                        action_type=template['action_type'],
                        specific_action=template['specific_action'],
                        example=template.get('example'),
                        related_score=compliance_result.compliance_score,
                        affects_compliance=True,
                        created_at=datetime.now().isoformat()
                    )
                    recommendations.append(rec)
        
        # Mandatory requirements recommendations
        for req_name, is_compliant in compliance_result.mandatory_requirements.items():
            if not is_compliant:
                template_key = self._map_requirement_to_template(req_name)
                if template_key and template_key in self.recommendation_templates:
                    template = self.recommendation_templates[template_key]
                    
                    rec = Recommendation(
                        id=f"mandatory_{req_name}",
                        title=template['title'],
                        description=template['description'],
                        category=template['category'],
                        priority='high',  # Mandatory requirements are high priority
                        impact=template['impact'],
                        effort=template['effort'],
                        action_type=template['action_type'],
                        specific_action=template['specific_action'],
                        example=template.get('example'),
                        related_score=compliance_result.compliance_score,
                        affects_compliance=True,
                        created_at=datetime.now().isoformat()
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def _generate_quality_recommendations(self, quality_metrics: QualityMetrics) -> List[Recommendation]:
        """Generate recommendations based on quality analysis"""
        
        recommendations = []
        
        # Completeness recommendations
        if quality_metrics.completeness_score < 70:
            for missing_element in quality_metrics.missing_elements[:5]:  # Top 5 missing
                rec = Recommendation(
                    id=f"completeness_{missing_element.replace(' ', '_').lower()}",
                    title=f"Adicionar: {missing_element}",
                    description=f"Incluir informação sobre {missing_element}",
                    category='quality',
                    priority='high' if quality_metrics.completeness_score < 50 else 'medium',
                    impact='high',
                    effort='medium',
                    action_type='add',
                    specific_action=f"Adicionar informação sobre {missing_element}",
                    related_score=quality_metrics.completeness_score,
                    affects_compliance=False,
                    created_at=datetime.now().isoformat()
                )
                recommendations.append(rec)
        
        # Clarity recommendations
        if quality_metrics.clarity_score < 70:
            rec = Recommendation(
                id="improve_clarity",
                title="Melhorar clareza do texto",
                description="Revisar e melhorar a estrutura e clareza do documento",
                category='quality',
                priority='medium',
                impact='medium',
                effort='medium',
                action_type='improve',
                specific_action="Reorganizar texto para maior clareza e usar linguagem jurídica adequada",
                example="Dividir em seções claras, usar frases mais objetivas",
                related_score=quality_metrics.clarity_score,
                affects_compliance=False,
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        # Information density recommendations
        if quality_metrics.information_score < 70:
            rec = Recommendation(
                id="increase_information_density",
                title="Adicionar mais detalhes informativos",
                description="Incluir mais informações relevantes sobre o imóvel e o processo",
                category='information',
                priority='medium',
                impact='medium',
                effort='low',
                action_type='add',
                specific_action="Adicionar características detalhadas do imóvel e informações financeiras",
                example="Área construída, número de cômodos, estado de conservação",
                related_score=quality_metrics.information_score,
                affects_compliance=False,
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_contextual_recommendations(self, quality_metrics: QualityMetrics,
                                           compliance_result: ComplianceResult,
                                           text: str) -> List[Recommendation]:
        """Generate contextual recommendations based on combined analysis"""
        
        recommendations = []
        
        # Overall quality is very low
        if quality_metrics.overall_score < 40:
            rec = Recommendation(
                id="comprehensive_revision",
                title="Revisão completa necessária",
                description="Documento requer revisão abrangente para atender padrões mínimos",
                category='quality',
                priority='critical',
                impact='high',
                effort='high',
                action_type='improve',
                specific_action="Realizar revisão completa do documento focando nos principais problemas identificados",
                related_score=quality_metrics.overall_score,
                affects_compliance=True,
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        # High compliance but low quality
        elif compliance_result.compliance_score > 80 and quality_metrics.overall_score < 60:
            rec = Recommendation(
                id="quality_enhancement",
                title="Melhorar qualidade geral",
                description="Documento está conforme, mas pode ter qualidade melhorada",
                category='quality',
                priority='medium',
                impact='medium',
                effort='medium',
                action_type='improve',
                specific_action="Focar em melhorar clareza e densidade de informações",
                related_score=quality_metrics.overall_score,
                affects_compliance=False,
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        # High quality but low compliance
        elif quality_metrics.overall_score > 80 and compliance_result.compliance_score < 60:
            rec = Recommendation(
                id="compliance_focus",
                title="Corrigir questões de conformidade",
                description="Documento tem boa qualidade mas precisa atender requisitos legais",
                category='compliance',
                priority='critical',
                impact='high',
                effort='low',
                action_type='fix',
                specific_action="Focar exclusivamente em resolver questões de conformidade legal",
                related_score=compliance_result.compliance_score,
                affects_compliance=True,
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _map_requirement_to_template(self, requirement_name: str) -> Optional[str]:
        """Map compliance requirement to recommendation template"""
        
        mapping = {
            'legal_reference': 'add_cpc_reference',
            'process_number': 'add_process_number',
            'property_address': 'add_property_address',
            'valuation_info': 'add_valuation',
            'minimum_bid': 'add_minimum_bid',
            'auction_datetime': 'add_auction_date',
            'qualification_deadline': 'add_qualification_deadline',
            'debt_amount': 'add_debt_information',
            'property_status': 'add_property_status'
        }
        
        return mapping.get(requirement_name)
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation], 
                                  recommendation_set: RecommendationSet):
        """Prioritize and organize recommendations"""
        
        for rec in recommendations:
            if rec.priority == 'critical':
                recommendation_set.critical_recommendations.append(rec)
            elif rec.priority == 'high':
                recommendation_set.high_priority_recommendations.append(rec)
            elif rec.priority == 'medium':
                recommendation_set.medium_priority_recommendations.append(rec)
            else:
                recommendation_set.low_priority_recommendations.append(rec)
        
        # Sort each priority level by impact and effort
        for priority_list in [recommendation_set.critical_recommendations,
                             recommendation_set.high_priority_recommendations,
                             recommendation_set.medium_priority_recommendations,
                             recommendation_set.low_priority_recommendations]:
            priority_list.sort(key=lambda x: (
                ['high', 'medium', 'low'].index(x.impact),
                ['low', 'medium', 'high'].index(x.effort)
            ))
    
    def _identify_quick_wins(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Identify quick wins (high impact, low effort)"""
        
        quick_wins = []
        for rec in recommendations:
            if rec.impact == 'high' and rec.effort == 'low':
                quick_wins.append(rec)
        
        return sorted(quick_wins, key=lambda x: x.priority == 'critical', reverse=True)
    
    def _create_action_plan(self, recommendation_set: RecommendationSet):
        """Create actionable plan with timeline"""
        
        # Immediate actions (critical and quick wins)
        immediate = []
        immediate.extend([r.specific_action for r in recommendation_set.critical_recommendations[:3]])
        immediate.extend([r.specific_action for r in recommendation_set.quick_wins[:2]])
        recommendation_set.immediate_actions = list(set(immediate))[:5]
        
        # Short-term actions (high priority)
        short_term = [r.specific_action for r in recommendation_set.high_priority_recommendations[:5]]
        recommendation_set.short_term_actions = short_term
        
        # Long-term actions (medium and low priority)
        long_term = []
        long_term.extend([r.specific_action for r in recommendation_set.medium_priority_recommendations[:3]])
        long_term.extend([r.specific_action for r in recommendation_set.low_priority_recommendations[:2]])
        recommendation_set.long_term_actions = long_term
    
    def _calculate_estimated_improvement(self, recommendation_set: RecommendationSet, 
                                       current_score: float) -> float:
        """Calculate estimated score improvement if recommendations are implemented"""
        
        total_impact = 0.0
        
        # Impact points based on priority and number of recommendations
        impact_weights = {
            'critical': 15,
            'high': 10,
            'medium': 5,
            'low': 2
        }
        
        total_impact += len(recommendation_set.critical_recommendations) * impact_weights['critical']
        total_impact += len(recommendation_set.high_priority_recommendations) * impact_weights['high']
        total_impact += len(recommendation_set.medium_priority_recommendations) * impact_weights['medium']
        total_impact += len(recommendation_set.low_priority_recommendations) * impact_weights['low']
        
        # Cap improvement at reasonable levels
        max_improvement = 100 - current_score
        estimated_improvement = min(total_impact, max_improvement)
        
        return estimated_improvement

# Global recommendation engine instance
recommendation_engine = RecommendationEngine()

def generate_document_recommendations(quality_metrics: QualityMetrics,
                                    compliance_result: ComplianceResult,
                                    text: str = "",
                                    job_id: str = "") -> RecommendationSet:
    """
    Convenience function for generating document recommendations
    
    Args:
        quality_metrics: Quality assessment results
        compliance_result: Compliance check results
        text: Original document text
        job_id: Job identifier for tracking
        
    Returns:
        RecommendationSet with prioritized recommendations
    """
    return recommendation_engine.generate_recommendations(
        quality_metrics, compliance_result, text, job_id
    )