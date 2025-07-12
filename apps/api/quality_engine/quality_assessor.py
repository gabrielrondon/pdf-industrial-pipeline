"""
Quality Assessor - Week 3 Implementation
Comprehensive quality assessment engine for Brazilian judicial auction documents
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for document assessment"""
    
    # Overall quality score (0-100)
    overall_score: float = 0.0
    quality_level: str = "Baixa"  # Baixa, Média, Boa, Excelente
    
    # Component scores (0-100 each)
    completeness_score: float = 0.0
    compliance_score: float = 0.0
    clarity_score: float = 0.0
    information_score: float = 0.0
    
    # Detailed analysis
    missing_elements: List[str] = None
    compliance_issues: List[str] = None
    quality_indicators: Dict[str, Any] = None
    improvement_potential: float = 0.0
    
    # Metadata
    assessment_timestamp: str = ""
    confidence_level: float = 0.0
    
    def __post_init__(self):
        if self.missing_elements is None:
            self.missing_elements = []
        if self.compliance_issues is None:
            self.compliance_issues = []
        if self.quality_indicators is None:
            self.quality_indicators = {}

class QualityAssessor:
    """
    Advanced quality assessment engine for Brazilian judicial auction documents
    Provides comprehensive 0-100 scoring with detailed analysis
    """
    
    def __init__(self):
        """Initialize quality assessment engine"""
        self.essential_elements = self._build_essential_elements()
        self.quality_patterns = self._build_quality_patterns()
        self.scoring_weights = self._build_scoring_weights()
        
        logger.info("Quality Assessor initialized with Brazilian legal standards")
    
    def _build_essential_elements(self) -> Dict[str, Dict[str, Any]]:
        """Build essential elements for Brazilian judicial auction documents"""
        return {
            'auction_identification': {
                'patterns': [
                    r'edital.*?leil[ãa]o',
                    r'hasta.*?p[úu]blica',
                    r'leil[ãa]o.*?judicial'
                ],
                'weight': 10,
                'description': 'Identificação do leilão/hasta pública'
            },
            'court_information': {
                'patterns': [
                    r'ju[íi]z.*?direito',
                    r'tribunal.*?justi[çc]a',
                    r'vara.*?c[íi]vel',
                    r'comarca.*?de'
                ],
                'weight': 8,
                'description': 'Informações do juízo/tribunal'
            },
            'process_number': {
                'patterns': [
                    r'\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}',  # New format
                    r'\d{3}\.\d{2}\.\d{4}\.\d{6}-\d{1}'        # Old format
                ],
                'weight': 9,
                'description': 'Número do processo judicial'
            },
            'parties': {
                'patterns': [
                    r'exequente.*?executado',
                    r'autor.*?r[ée]u',
                    r'requerente.*?requerido'
                ],
                'weight': 7,
                'description': 'Partes do processo (exequente/executado)'
            },
            'property_description': {
                'patterns': [
                    r'im[óo]vel.*?situado',
                    r'apartamento.*?n[°º]',
                    r'casa.*?localizada',
                    r'terreno.*?medindo'
                ],
                'weight': 10,
                'description': 'Descrição detalhada do imóvel'
            },
            'property_address': {
                'patterns': [
                    r'rua.*?\d+',
                    r'avenida.*?\d+',
                    r'pra[çc]a.*?\d+',
                    r'alameda.*?\d+'
                ],
                'weight': 9,
                'description': 'Endereço completo do imóvel'
            },
            'property_registration': {
                'patterns': [
                    r'matr[íi]cula.*?n[°º].*?\d+',
                    r'registro.*?im[óo]veis',
                    r'cart[óo]rio.*?registro'
                ],
                'weight': 8,
                'description': 'Matrícula/registro do imóvel'
            },
            'valuation': {
                'patterns': [
                    r'valor.*?avalia[çc][ãa]o.*?R\$',
                    r'avalia[çc][ãa]o.*?R\$.*?\d+'
                ],
                'weight': 9,
                'description': 'Valor da avaliação do imóvel'
            },
            'minimum_bid': {
                'patterns': [
                    r'lance.*?m[íi]nimo.*?R\$',
                    r'valor.*?m[íi]nimo.*?R\$'
                ],
                'weight': 9,
                'description': 'Lance mínimo do leilão'
            },
            'debt_amount': {
                'patterns': [
                    r'd[ée]bito.*?total.*?R\$',
                    r'd[íi]vida.*?R\$.*?\d+'
                ],
                'weight': 7,
                'description': 'Valor do débito total'
            },
            'auction_date': {
                'patterns': [
                    r'data.*?leil[ãa]o.*?\d{1,2}/\d{1,2}/\d{4}',
                    r'leil[ãa]o.*?\d{1,2}.*?de.*?\d{4}',
                    r'\d{1,2}/\d{1,2}/\d{4}.*?leil[ãa]o'
                ],
                'weight': 8,
                'description': 'Data do leilão'
            },
            'auction_time': {
                'patterns': [
                    r'\d{1,2}[h:]\d{2}.*?horas?',
                    r'[àa]s.*?\d{1,2}[h:]\d{2}'
                ],
                'weight': 6,
                'description': 'Horário do leilão'
            },
            'auction_location': {
                'patterns': [
                    r'local.*?leil[ãa]o',
                    r'forum.*?central',
                    r'sala.*?leil[ões]+'
                ],
                'weight': 7,
                'description': 'Local do leilão'
            },
            'legal_references': {
                'patterns': [
                    r'art\.?\s*889.*?cpc',
                    r'c[óo]digo.*?processo.*?civil',
                    r'lei.*?n[°º].*?\d+'
                ],
                'weight': 8,
                'description': 'Referências legais (CPC, leis)'
            },
            'property_status': {
                'patterns': [
                    r'livre.*?ocupa[çc][ãa]o',
                    r'ocupado.*?inquilino',
                    r'situa[çc][ãa]o.*?im[óo]vel'
                ],
                'weight': 6,
                'description': 'Situação atual do imóvel'
            }
        }
    
    def _build_quality_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for quality assessment"""
        return {
            'high_quality_indicators': [
                r'documentação.*?regular',
                r'certidão.*?atualizada',
                r'livre.*?[ôo]nus',
                r'sem.*?pendências',
                r'regularmente.*?intimado',
                r'devidamente.*?publicado'
            ],
            'medium_quality_indicators': [
                r'documentação.*?pendente',
                r'aguardando.*?certidão',
                r'em.*?regularização',
                r'processo.*?andamento'
            ],
            'low_quality_indicators': [
                r'documentação.*?irregular',
                r'pendências.*?cartório',
                r'problemas.*?registro',
                r'informação.*?incompleta',
                r'dados.*?insuficientes'
            ],
            'clarity_indicators': [
                r'conforme.*?estabelece',
                r'nos.*?termos.*?lei',
                r'de.*?acordo.*?disposto',
                r'em.*?cumprimento'
            ],
            'information_density_indicators': [
                r'metragem.*?\d+.*?m[²2]',
                r'dormit[óo]rios?.*?\d+',
                r'vagas?.*?garagem.*?\d+',
                r'área.*?construída.*?\d+'
            ]
        }
    
    def _build_scoring_weights(self) -> Dict[str, float]:
        """Build scoring weights for quality components"""
        return {
            'completeness': 0.25,  # 25% - Essential information presence
            'compliance': 0.30,    # 30% - Legal requirement adherence  
            'clarity': 0.20,       # 20% - Text readability and structure
            'information': 0.25    # 25% - Information density and usefulness
        }
    
    def assess_quality(self, text: str, 
                      enhanced_features: Optional[Dict] = None,
                      job_id: str = "") -> QualityMetrics:
        """
        Perform comprehensive quality assessment of document
        
        Args:
            text: Document text to assess
            enhanced_features: Optional enhanced features from Week 1
            job_id: Job identifier for tracking
            
        Returns:
            QualityMetrics with comprehensive quality analysis
        """
        start_time = datetime.now()
        
        try:
            # Initialize quality metrics
            metrics = QualityMetrics(
                assessment_timestamp=start_time.isoformat()
            )
            
            # 1. Assess completeness (25%)
            completeness_score, missing_elements = self._assess_completeness(text)
            metrics.completeness_score = completeness_score
            metrics.missing_elements = missing_elements
            
            # 2. Assess compliance (30%) 
            compliance_score, compliance_issues = self._assess_compliance(text, enhanced_features)
            metrics.compliance_score = compliance_score
            metrics.compliance_issues = compliance_issues
            
            # 3. Assess clarity (20%)
            clarity_score = self._assess_clarity(text)
            metrics.clarity_score = clarity_score
            
            # 4. Assess information density (25%)
            information_score, quality_indicators = self._assess_information_density(text)
            metrics.information_score = information_score
            metrics.quality_indicators = quality_indicators
            
            # 5. Calculate overall score
            weights = self.scoring_weights
            metrics.overall_score = (
                completeness_score * weights['completeness'] +
                compliance_score * weights['compliance'] +
                clarity_score * weights['clarity'] +
                information_score * weights['information']
            )
            
            # 6. Determine quality level
            metrics.quality_level = self._determine_quality_level(metrics.overall_score)
            
            # 7. Calculate improvement potential
            metrics.improvement_potential = 100 - metrics.overall_score
            
            # 8. Calculate confidence level
            metrics.confidence_level = self._calculate_confidence(text, metrics)
            
            logger.info(f"Quality assessment completed for {job_id}: "
                       f"overall={metrics.overall_score:.1f}, "
                       f"level={metrics.quality_level}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in quality assessment for {job_id}: {e}")
            return QualityMetrics(
                overall_score=0.0,
                quality_level="Erro",
                assessment_timestamp=start_time.isoformat(),
                confidence_level=0.0
            )
    
    def _assess_completeness(self, text: str) -> Tuple[float, List[str]]:
        """Assess document completeness based on essential elements"""
        
        total_weight = sum(element['weight'] for element in self.essential_elements.values())
        found_weight = 0
        missing_elements = []
        
        text_lower = text.lower()
        
        for element_name, element_info in self.essential_elements.items():
            found = False
            
            for pattern in element_info['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found = True
                    break
            
            if found:
                found_weight += element_info['weight']
            else:
                missing_elements.append(element_info['description'])
        
        completeness_score = (found_weight / total_weight) * 100
        return completeness_score, missing_elements
    
    def _assess_compliance(self, text: str, enhanced_features: Optional[Dict] = None) -> Tuple[float, List[str]]:
        """Assess legal compliance with Brazilian regulations"""
        
        compliance_score = 100.0
        compliance_issues = []
        
        text_lower = text.lower()
        
        # Check CPC Article 889 compliance
        cpc_889_requirements = [
            (r'art\.?\s*889.*?cpc|código.*?processo.*?civil', 
             'Referência ao art. 889 do CPC obrigatória'),
            (r'hasta.*?pública|leilão.*?judicial', 
             'Identificação clara como hasta pública/leilão judicial'),
            (r'prazo.*?\d+.*?dias?|até.*?\d+.*?dias?', 
             'Prazo para habilitação deve ser especificado'),
            (r'valor.*?avaliação.*?R\$|avaliação.*?R\$.*?\d+', 
             'Valor da avaliação deve ser informado'),
            (r'lance.*?mínimo.*?R\$|mínimo.*?R\$.*?\d+', 
             'Lance mínimo deve ser especificado')
        ]
        
        for pattern, requirement in cpc_889_requirements:
            if not re.search(pattern, text_lower, re.IGNORECASE):
                compliance_score -= 15  # Each missing requirement = -15 points
                compliance_issues.append(requirement)
        
        # Check property description compliance
        property_requirements = [
            (r'matrícula.*?n[°º].*?\d+|registro.*?imóveis', 
             'Matrícula do imóvel deve ser informada'),
            (r'rua.*?\d+|avenida.*?\d+|endereço.*?completo', 
             'Endereço completo deve ser fornecido'),
            (r'situação.*?imóvel|ocupação.*?imóvel', 
             'Situação atual do imóvel deve ser descrita')
        ]
        
        for pattern, requirement in property_requirements:
            if not re.search(pattern, text_lower, re.IGNORECASE):
                compliance_score -= 10  # Each missing requirement = -10 points
                compliance_issues.append(requirement)
        
        # Check procedural compliance
        procedural_requirements = [
            (r'processo.*?n[°º].*?\d+|autos.*?n[°º].*?\d+', 
             'Número do processo deve ser informado'),
            (r'exequente.*?executado|autor.*?réu', 
             'Partes do processo devem ser identificadas'),
            (r'data.*?leilão.*?\d+|leilão.*?\d{1,2}/\d{1,2}/\d{4}', 
             'Data do leilão deve ser especificada')
        ]
        
        for pattern, requirement in procedural_requirements:
            if not re.search(pattern, text_lower, re.IGNORECASE):
                compliance_score -= 8  # Each missing requirement = -8 points
                compliance_issues.append(requirement)
        
        # Use enhanced features if available
        if enhanced_features:
            # Bonus for high legal pattern recognition
            if enhanced_features.get('legal_patterns', 0) > 5:
                compliance_score += 5
            
            # Bonus for proper process number format
            if enhanced_features.get('processo_numbers', 0) > 0:
                compliance_score += 10
        
        return max(0.0, min(100.0, compliance_score)), compliance_issues
    
    def _assess_clarity(self, text: str) -> float:
        """Assess text clarity and readability"""
        
        if not text:
            return 0.0
        
        clarity_score = 50.0  # Base score
        text_lower = text.lower()
        
        # Positive clarity indicators
        for pattern in self.quality_patterns['clarity_indicators']:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            clarity_score += min(matches * 5, 20)  # Max +20 points
        
        # Text structure analysis
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Optimal sentence length: 15-25 words
            if 15 <= avg_sentence_length <= 25:
                clarity_score += 10
            elif 10 <= avg_sentence_length <= 30:
                clarity_score += 5
            else:
                clarity_score -= 5
        
        # Paragraph structure
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            clarity_score += 10  # Well-structured document
        
        # Proper capitalization and formatting
        if re.search(r'^[A-Z]', text.strip()):
            clarity_score += 5
        
        # Legal terminology usage (proper legal language)
        legal_terms = ['artigo', 'parágrafo', 'inciso', 'conforme', 'estabelece']
        for term in legal_terms:
            if term in text_lower:
                clarity_score += 2
        
        return max(0.0, min(100.0, clarity_score))
    
    def _assess_information_density(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Assess information density and usefulness"""
        
        if not text:
            return 0.0, {}
        
        density_score = 40.0  # Base score
        quality_indicators = {}
        text_lower = text.lower()
        
        # High-value information indicators
        for pattern in self.quality_patterns['information_density_indicators']:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            if matches > 0:
                density_score += min(matches * 8, 24)  # Max +24 points
                quality_indicators[pattern] = matches
        
        # Financial information density
        currency_patterns = [
            r'R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}',
            r'\d+\s*mil\s*reais',
            r'\d+\s*milhões?\s*de\s*reais'
        ]
        
        financial_info_count = 0
        for pattern in currency_patterns:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            financial_info_count += matches
        
        if financial_info_count >= 3:
            density_score += 15  # Rich financial information
        elif financial_info_count >= 1:
            density_score += 8
        
        quality_indicators['financial_info_count'] = financial_info_count
        
        # Property details density
        property_details = [
            r'\d+\s*m[²2]',  # Area in square meters
            r'\d+\s*dormitórios?',  # Bedrooms
            r'\d+\s*banheiros?',  # Bathrooms
            r'vaga.*?garagem',  # Parking
            r'andar.*?\d+',  # Floor number
        ]
        
        property_detail_count = 0
        for pattern in property_details:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            property_detail_count += matches
        
        if property_detail_count >= 3:
            density_score += 12
        elif property_detail_count >= 1:
            density_score += 6
        
        quality_indicators['property_detail_count'] = property_detail_count
        
        # Information vs text ratio
        words = text.split()
        if len(words) > 0:
            info_ratio = (financial_info_count + property_detail_count) / len(words) * 100
            if info_ratio > 5:
                density_score += 10
            elif info_ratio > 2:
                density_score += 5
            
            quality_indicators['information_ratio'] = info_ratio
        
        return max(0.0, min(100.0, density_score)), quality_indicators
    
    def _determine_quality_level(self, overall_score: float) -> str:
        """Determine quality level based on overall score"""
        
        if overall_score >= 85:
            return "Excelente"
        elif overall_score >= 70:
            return "Boa"
        elif overall_score >= 50:
            return "Média"
        else:
            return "Baixa"
    
    def _calculate_confidence(self, text: str, metrics: QualityMetrics) -> float:
        """Calculate confidence level in the assessment"""
        
        confidence = 0.8  # Base confidence
        
        # Text length factor
        if len(text) > 500:
            confidence += 0.1
        elif len(text) < 100:
            confidence -= 0.2
        
        # Completeness factor
        if metrics.completeness_score > 80:
            confidence += 0.1
        elif metrics.completeness_score < 30:
            confidence -= 0.1
        
        # Consistency check
        score_variance = abs(metrics.completeness_score - metrics.compliance_score)
        if score_variance > 30:
            confidence -= 0.1  # Inconsistent scores reduce confidence
        
        return max(0.0, min(1.0, confidence))
    
    def get_quality_insights(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Generate quality insights and recommendations"""
        
        insights = {
            'strengths': [],
            'weaknesses': [],
            'priority_actions': [],
            'improvement_suggestions': []
        }
        
        # Identify strengths
        if metrics.completeness_score >= 80:
            insights['strengths'].append("Documento contém informações essenciais completas")
        
        if metrics.compliance_score >= 80:
            insights['strengths'].append("Alta conformidade com requisitos legais")
        
        if metrics.clarity_score >= 80:
            insights['strengths'].append("Texto claro e bem estruturado")
        
        if metrics.information_score >= 80:
            insights['strengths'].append("Rica densidade de informações úteis")
        
        # Identify weaknesses
        if metrics.completeness_score < 50:
            insights['weaknesses'].append("Informações essenciais ausentes")
        
        if metrics.compliance_score < 50:
            insights['weaknesses'].append("Não conformidade com requisitos legais")
        
        if metrics.clarity_score < 50:
            insights['weaknesses'].append("Texto confuso ou mal estruturado")
        
        if metrics.information_score < 50:
            insights['weaknesses'].append("Baixa densidade de informações úteis")
        
        # Priority actions (based on lowest scores)
        scores = {
            'completeness': metrics.completeness_score,
            'compliance': metrics.compliance_score,
            'clarity': metrics.clarity_score,
            'information': metrics.information_score
        }
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        if sorted_scores[0][1] < 70:
            if sorted_scores[0][0] == 'completeness':
                insights['priority_actions'].append("Adicionar informações essenciais em falta")
            elif sorted_scores[0][0] == 'compliance':
                insights['priority_actions'].append("Corrigir questões de conformidade legal")
            elif sorted_scores[0][0] == 'clarity':
                insights['priority_actions'].append("Melhorar clareza e estrutura do texto")
            elif sorted_scores[0][0] == 'information':
                insights['priority_actions'].append("Adicionar mais detalhes informativos")
        
        # Improvement suggestions
        if metrics.missing_elements:
            insights['improvement_suggestions'].extend([
                f"Adicionar: {element}" for element in metrics.missing_elements[:3]
            ])
        
        if metrics.compliance_issues:
            insights['improvement_suggestions'].extend([
                f"Corrigir: {issue}" for issue in metrics.compliance_issues[:3]
            ])
        
        return insights

# Global assessor instance
quality_assessor = QualityAssessor()

def assess_document_quality(text: str, 
                           enhanced_features: Optional[Dict] = None,
                           job_id: str = "") -> QualityMetrics:
    """
    Convenience function for document quality assessment
    
    Args:
        text: Document text to assess
        enhanced_features: Optional enhanced features from Week 1
        job_id: Job identifier for tracking
        
    Returns:
        QualityMetrics with comprehensive quality analysis
    """
    return quality_assessor.assess_quality(text, enhanced_features, job_id)

def get_quality_insights(metrics: QualityMetrics) -> Dict[str, Any]:
    """
    Convenience function for quality insights
    
    Args:
        metrics: QualityMetrics from assessment
        
    Returns:
        Quality insights and recommendations
    """
    return quality_assessor.get_quality_insights(metrics)