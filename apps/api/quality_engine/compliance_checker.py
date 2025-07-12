"""
Compliance Checker - Week 3 Implementation
Brazilian legal compliance validation for judicial auction documents
Focuses on CPC Article 889 and Brazilian auction regulations
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

@dataclass
class ComplianceResult:
    """Compliance check result with detailed analysis"""
    
    # Overall compliance
    is_compliant: bool = False
    compliance_score: float = 0.0  # 0-100
    compliance_level: str = "Não Conforme"  # Não Conforme, Parcial, Conforme
    
    # CPC Article 889 compliance
    cpc_889_compliance: Dict[str, Any] = None
    
    # Requirement compliance
    mandatory_requirements: Dict[str, bool] = None
    optional_requirements: Dict[str, bool] = None
    
    # Issues and violations
    violations: List[Dict[str, str]] = None
    warnings: List[Dict[str, str]] = None
    recommendations: List[str] = None
    
    # Metadata
    check_timestamp: str = ""
    confidence_level: float = 0.0
    
    def __post_init__(self):
        if self.cpc_889_compliance is None:
            self.cpc_889_compliance = {}
        if self.mandatory_requirements is None:
            self.mandatory_requirements = {}
        if self.optional_requirements is None:
            self.optional_requirements = {}
        if self.violations is None:
            self.violations = []
        if self.warnings is None:
            self.warnings = []
        if self.recommendations is None:
            self.recommendations = []

class ComplianceChecker:
    """
    Brazilian legal compliance checker for judicial auction documents
    Validates against CPC Article 889 and auction regulations
    """
    
    def __init__(self):
        """Initialize compliance checker with Brazilian legal requirements"""
        self.cpc_889_requirements = self._build_cpc_889_requirements()
        self.mandatory_requirements = self._build_mandatory_requirements()
        self.optional_requirements = self._build_optional_requirements()
        self.legal_patterns = self._build_legal_patterns()
        
        logger.info("Compliance Checker initialized with CPC Article 889 requirements")
    
    def _build_cpc_889_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Build CPC Article 889 specific requirements"""
        return {
            'legal_reference': {
                'patterns': [
                    r'art\.?\s*889.*?cpc',
                    r'artigo\s*889.*?código.*?processo.*?civil',
                    r'nos\s*termos.*?art\.?\s*889'
                ],
                'description': 'Referência expressa ao art. 889 do CPC',
                'severity': 'critical',
                'points': 20
            },
            'hasta_publica_declaration': {
                'patterns': [
                    r'será\s*realizada?\s*hasta\s*pública',
                    r'leilão\s*judicial',
                    r'hasta\s*pública.*?judicial'
                ],
                'description': 'Declaração de hasta pública/leilão judicial',
                'severity': 'critical',
                'points': 20
            },
            'public_notice': {
                'patterns': [
                    r'torna\s*público\s*que',
                    r'faz\s*saber\s*aos',
                    r'edital.*?público'
                ],
                'description': 'Comunicação pública do leilão',
                'severity': 'high',
                'points': 15
            },
            'property_description': {
                'patterns': [
                    r'imóvel.*?situado',
                    r'bem.*?descrito',
                    r'propriedade.*?localizada'
                ],
                'description': 'Descrição clara do bem a ser leiloado',
                'severity': 'critical',
                'points': 20
            },
            'valuation_info': {
                'patterns': [
                    r'valor.*?avaliação.*?R\$',
                    r'avaliação.*?R\$.*?\d+',
                    r'avaliado.*?em.*?R\$'
                ],
                'description': 'Valor da avaliação do bem',
                'severity': 'critical',
                'points': 15
            },
            'minimum_bid': {
                'patterns': [
                    r'lance.*?mínimo.*?R\$',
                    r'valor.*?mínimo.*?R\$',
                    r'base.*?licitação.*?R\$'
                ],
                'description': 'Lance mínimo para participação',
                'severity': 'critical',
                'points': 15
            },
            'qualification_deadline': {
                'patterns': [
                    r'prazo.*?\d+.*?dias.*?habilitação',
                    r'habilitação.*?até.*?\d+.*?dias',
                    r'qualificação.*?prazo.*?\d+'
                ],
                'description': 'Prazo para habilitação de interessados',
                'severity': 'high',
                'points': 10
            }
        }
    
    def _build_mandatory_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Build mandatory requirements for auction documents"""
        return {
            'court_identification': {
                'patterns': [
                    r'juiz.*?direito.*?vara',
                    r'tribunal.*?justiça',
                    r'comarca.*?de'
                ],
                'description': 'Identificação do juízo/tribunal',
                'points': 10
            },
            'process_number': {
                'patterns': [
                    r'\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}',  # New CNJ format
                    r'\d{3}\.\d{2}\.\d{4}\.\d{6}-\d{1}',        # Old format
                    r'processo.*?n[°º].*?\d+'
                ],
                'description': 'Número do processo judicial',
                'points': 15
            },
            'parties_identification': {
                'patterns': [
                    r'exequente.*?executado',
                    r'autor.*?réu',
                    r'requerente.*?requerido'
                ],
                'description': 'Identificação das partes processuais',
                'points': 10
            },
            'property_address': {
                'patterns': [
                    r'rua.*?\d+',
                    r'avenida.*?\d+',
                    r'endereço.*?completo',
                    r'localizado.*?na'
                ],
                'description': 'Endereço completo do imóvel',
                'points': 15
            },
            'property_registration': {
                'patterns': [
                    r'matrícula.*?n[°º].*?\d+',
                    r'registro.*?imóveis.*?\d+',
                    r'cartório.*?registro'
                ],
                'description': 'Matrícula/registro do imóvel',
                'points': 10
            },
            'auction_datetime': {
                'patterns': [
                    r'data.*?leilão.*?\d{1,2}/\d{1,2}/\d{4}',
                    r'leilão.*?\d{1,2}.*?de.*?\d{4}',
                    r'\d{1,2}/\d{1,2}/\d{4}.*?\d{1,2}[h:]\d{2}'
                ],
                'description': 'Data e horário do leilão',
                'points': 15
            },
            'auction_location': {
                'patterns': [
                    r'local.*?leilão',
                    r'fórum.*?central',
                    r'sala.*?leilões?',
                    r'endereço.*?leilão'
                ],
                'description': 'Local onde será realizado o leilão',
                'points': 10
            }
        }
    
    def _build_optional_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Build optional but recommended requirements"""
        return {
            'debt_amount': {
                'patterns': [
                    r'débito.*?total.*?R\$',
                    r'dívida.*?R\$.*?\d+',
                    r'valor.*?executado.*?R\$'
                ],
                'description': 'Valor total do débito',
                'points': 5
            },
            'property_status': {
                'patterns': [
                    r'livre.*?ocupação',
                    r'ocupado.*?inquilino',
                    r'situação.*?imóvel'
                ],
                'description': 'Situação atual do imóvel',
                'points': 5
            },
            'encumbrances': {
                'patterns': [
                    r'ônus.*?gravames',
                    r'hipoteca.*?favor',
                    r'livre.*?ônus'
                ],
                'description': 'Informações sobre ônus e gravames',
                'points': 5
            },
            'payment_conditions': {
                'patterns': [
                    r'pagamento.*?vista',
                    r'condições.*?pagamento',
                    r'parcelamento.*?permitido'
                ],
                'description': 'Condições de pagamento',
                'points': 3
            },
            'contact_information': {
                'patterns': [
                    r'informações.*?telefone',
                    r'contato.*?\d{2}\s*\d{4,5}-\d{4}',
                    r'esclarecimentos.*?fone'
                ],
                'description': 'Informações de contato',
                'points': 3
            },
            'inspection_schedule': {
                'patterns': [
                    r'visitação.*?imóvel',
                    r'vistoria.*?agendar',
                    r'inspeção.*?prévia'
                ],
                'description': 'Agendamento de visitação',
                'points': 2
            }
        }
    
    def _build_legal_patterns(self) -> Dict[str, List[str]]:
        """Build legal compliance patterns"""
        return {
            'formal_language': [
                r'nos\s*termos.*?lei',
                r'conforme\s*estabelece',
                r'de\s*acordo.*?disposto',
                r'em\s*cumprimento.*?determinação'
            ],
            'legal_procedures': [
                r'intimação.*?regular',
                r'citação.*?devida',
                r'publicação.*?oficial',
                r'notificação.*?legal'
            ],
            'time_compliance': [
                r'prazo.*?legal',
                r'antecedência.*?\d+.*?dias',
                r'tempo.*?hábil'
            ]
        }
    
    def check_compliance(self, text: str, 
                        enhanced_features: Optional[Dict] = None,
                        job_id: str = "") -> ComplianceResult:
        """
        Perform comprehensive compliance check
        
        Args:
            text: Document text to check
            enhanced_features: Optional enhanced features from Week 1
            job_id: Job identifier for tracking
            
        Returns:
            ComplianceResult with detailed compliance analysis
        """
        start_time = datetime.now()
        
        try:
            # Initialize compliance result
            result = ComplianceResult(
                check_timestamp=start_time.isoformat()
            )
            
            # 1. Check CPC Article 889 compliance
            cpc_score, cpc_details = self._check_cpc_889_compliance(text)
            result.cpc_889_compliance = cpc_details
            
            # 2. Check mandatory requirements
            mandatory_score, mandatory_details = self._check_mandatory_requirements(text)
            result.mandatory_requirements = mandatory_details
            
            # 3. Check optional requirements
            optional_score, optional_details = self._check_optional_requirements(text)
            result.optional_requirements = optional_details
            
            # 4. Identify violations and warnings
            violations, warnings = self._identify_violations_warnings(text, result)
            result.violations = violations
            result.warnings = warnings
            
            # 5. Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
            # 6. Calculate overall compliance score
            # CPC 889: 60%, Mandatory: 30%, Optional: 10%
            result.compliance_score = (
                cpc_score * 0.60 +
                mandatory_score * 0.30 +
                optional_score * 0.10
            )
            
            # 7. Determine compliance level
            result.compliance_level = self._determine_compliance_level(result.compliance_score)
            result.is_compliant = result.compliance_score >= 80
            
            # 8. Calculate confidence level
            result.confidence_level = self._calculate_confidence(text, result)
            
            logger.info(f"Compliance check completed for {job_id}: "
                       f"score={result.compliance_score:.1f}, "
                       f"level={result.compliance_level}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in compliance check for {job_id}: {e}")
            return ComplianceResult(
                is_compliant=False,
                compliance_score=0.0,
                compliance_level="Erro",
                check_timestamp=start_time.isoformat(),
                confidence_level=0.0
            )
    
    def _check_cpc_889_compliance(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Check compliance with CPC Article 889 requirements"""
        
        total_points = sum(req['points'] for req in self.cpc_889_requirements.values())
        achieved_points = 0
        details = {}
        
        text_lower = text.lower()
        
        for req_name, req_info in self.cpc_889_requirements.items():
            found = False
            matched_pattern = None
            
            for pattern in req_info['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found = True
                    matched_pattern = pattern
                    break
            
            if found:
                achieved_points += req_info['points']
                details[req_name] = {
                    'compliant': True,
                    'matched_pattern': matched_pattern,
                    'description': req_info['description'],
                    'points': req_info['points']
                }
            else:
                details[req_name] = {
                    'compliant': False,
                    'description': req_info['description'],
                    'severity': req_info['severity'],
                    'points': 0
                }
        
        score = (achieved_points / total_points) * 100
        return score, details
    
    def _check_mandatory_requirements(self, text: str) -> Tuple[float, Dict[str, bool]]:
        """Check mandatory requirements compliance"""
        
        total_points = sum(req['points'] for req in self.mandatory_requirements.values())
        achieved_points = 0
        details = {}
        
        text_lower = text.lower()
        
        for req_name, req_info in self.mandatory_requirements.items():
            found = False
            
            for pattern in req_info['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found = True
                    break
            
            if found:
                achieved_points += req_info['points']
            
            details[req_name] = found
        
        score = (achieved_points / total_points) * 100
        return score, details
    
    def _check_optional_requirements(self, text: str) -> Tuple[float, Dict[str, bool]]:
        """Check optional requirements compliance"""
        
        total_points = sum(req['points'] for req in self.optional_requirements.values())
        achieved_points = 0
        details = {}
        
        text_lower = text.lower()
        
        for req_name, req_info in self.optional_requirements.items():
            found = False
            
            for pattern in req_info['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found = True
                    break
            
            if found:
                achieved_points += req_info['points']
            
            details[req_name] = found
        
        score = (achieved_points / total_points) * 100 if total_points > 0 else 100
        return score, details
    
    def _identify_violations_warnings(self, text: str, result: ComplianceResult) -> Tuple[List[Dict], List[Dict]]:
        """Identify compliance violations and warnings"""
        
        violations = []
        warnings = []
        
        # Critical violations (CPC 889 non-compliance)
        for req_name, req_details in result.cpc_889_compliance.items():
            if not req_details.get('compliant', False):
                severity = req_details.get('severity', 'medium')
                
                violation = {
                    'type': 'cpc_889_violation',
                    'requirement': req_name,
                    'description': req_details['description'],
                    'severity': severity,
                    'category': 'legal_compliance'
                }
                
                if severity == 'critical':
                    violations.append(violation)
                else:
                    warnings.append(violation)
        
        # Mandatory requirement violations
        for req_name, is_compliant in result.mandatory_requirements.items():
            if not is_compliant:
                req_info = self.mandatory_requirements[req_name]
                violations.append({
                    'type': 'mandatory_violation',
                    'requirement': req_name,
                    'description': req_info['description'],
                    'severity': 'high',
                    'category': 'mandatory_requirement'
                })
        
        # Optional requirement warnings
        missing_optional = []
        for req_name, is_compliant in result.optional_requirements.items():
            if not is_compliant:
                missing_optional.append(req_name)
        
        if len(missing_optional) > 3:  # Too many missing optional requirements
            warnings.append({
                'type': 'optional_deficiency',
                'description': f'Muitos requisitos opcionais ausentes: {len(missing_optional)}',
                'severity': 'medium',
                'category': 'optional_requirement'
            })
        
        return violations, warnings
    
    def _generate_recommendations(self, result: ComplianceResult) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        # CPC 889 recommendations
        for req_name, req_details in result.cpc_889_compliance.items():
            if not req_details.get('compliant', False):
                if req_name == 'legal_reference':
                    recommendations.append("Incluir referência expressa ao art. 889 do CPC")
                elif req_name == 'hasta_publica_declaration':
                    recommendations.append("Declarar explicitamente que se trata de hasta pública/leilão judicial")
                elif req_name == 'public_notice':
                    recommendations.append("Adicionar comunicação pública do leilão ('torna público que')")
                elif req_name == 'property_description':
                    recommendations.append("Incluir descrição detalhada do imóvel a ser leiloado")
                elif req_name == 'valuation_info':
                    recommendations.append("Informar o valor da avaliação do imóvel")
                elif req_name == 'minimum_bid':
                    recommendations.append("Especificar o lance mínimo para participação")
                elif req_name == 'qualification_deadline':
                    recommendations.append("Estabelecer prazo para habilitação de interessados")
        
        # Mandatory requirement recommendations
        for req_name, is_compliant in result.mandatory_requirements.items():
            if not is_compliant:
                req_info = self.mandatory_requirements[req_name]
                recommendations.append(f"Adicionar: {req_info['description']}")
        
        # Priority recommendations based on compliance score
        if result.compliance_score < 50:
            recommendations.insert(0, "URGENTE: Documento não atende aos requisitos mínimos legais")
        elif result.compliance_score < 70:
            recommendations.insert(0, "IMPORTANTE: Corrigir questões de conformidade antes da publicação")
        
        # General improvement recommendations
        if len(result.violations) > 3:
            recommendations.append("Revisar todo o documento para conformidade legal")
        
        if len(result.warnings) > 2:
            recommendations.append("Considerar adicionar informações opcionais para melhor qualidade")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _determine_compliance_level(self, compliance_score: float) -> str:
        """Determine compliance level based on score"""
        
        if compliance_score >= 90:
            return "Totalmente Conforme"
        elif compliance_score >= 80:
            return "Conforme"
        elif compliance_score >= 60:
            return "Parcialmente Conforme"
        elif compliance_score >= 40:
            return "Baixa Conformidade"
        else:
            return "Não Conforme"
    
    def _calculate_confidence(self, text: str, result: ComplianceResult) -> float:
        """Calculate confidence in compliance assessment"""
        
        confidence = 0.85  # Base confidence
        
        # Text length factor
        if len(text) > 1000:
            confidence += 0.1
        elif len(text) < 200:
            confidence -= 0.2
        
        # Pattern matching clarity
        cpc_compliant_count = sum(1 for details in result.cpc_889_compliance.values() 
                                 if details.get('compliant', False))
        if cpc_compliant_count > 4:
            confidence += 0.05
        
        # Consistency check
        if result.compliance_score > 80 and len(result.violations) > 2:
            confidence -= 0.1  # Inconsistent results
        
        return max(0.0, min(1.0, confidence))
    
    def get_compliance_summary(self, result: ComplianceResult) -> Dict[str, Any]:
        """Generate compliance summary for reporting"""
        
        return {
            'overall_status': {
                'is_compliant': result.is_compliant,
                'compliance_score': result.compliance_score,
                'compliance_level': result.compliance_level,
                'confidence': result.confidence_level
            },
            'cpc_889_status': {
                'requirements_met': sum(1 for details in result.cpc_889_compliance.values() 
                                      if details.get('compliant', False)),
                'total_requirements': len(result.cpc_889_compliance),
                'critical_violations': len([v for v in result.violations 
                                          if v.get('severity') == 'critical'])
            },
            'requirement_status': {
                'mandatory_met': sum(1 for compliant in result.mandatory_requirements.values() if compliant),
                'mandatory_total': len(result.mandatory_requirements),
                'optional_met': sum(1 for compliant in result.optional_requirements.values() if compliant),
                'optional_total': len(result.optional_requirements)
            },
            'issues': {
                'violations_count': len(result.violations),
                'warnings_count': len(result.warnings),
                'recommendations_count': len(result.recommendations)
            },
            'next_steps': result.recommendations[:3] if result.recommendations else []
        }

# Global compliance checker instance
compliance_checker = ComplianceChecker()

def check_document_compliance(text: str, 
                             enhanced_features: Optional[Dict] = None,
                             job_id: str = "") -> ComplianceResult:
    """
    Convenience function for document compliance checking
    
    Args:
        text: Document text to check
        enhanced_features: Optional enhanced features from Week 1
        job_id: Job identifier for tracking
        
    Returns:
        ComplianceResult with detailed compliance analysis
    """
    return compliance_checker.check_compliance(text, enhanced_features, job_id)

def get_compliance_summary(result: ComplianceResult) -> Dict[str, Any]:
    """
    Convenience function for compliance summary
    
    Args:
        result: ComplianceResult from compliance check
        
    Returns:
        Compliance summary for reporting
    """
    return compliance_checker.get_compliance_summary(result)