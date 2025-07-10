"""
Main judicial auction analyzer that combines all components
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import (
    JudicialAnalysisResult, AuctionType, ComplianceStatus,
    PropertyOccupancyStatus, ValuationAnalysis, DebtAnalysis,
    PropertyStatus, LegalRestrictions, PublicationCompliance,
    NotificationStatus
)
from .date_parser import DateParser, DeadlineCalculator
from .financial_analyzer import FinancialAnalyzer
from .compliance_checker import ComplianceChecker
from .property_analyzer import PropertyAnalyzer

logger = logging.getLogger(__name__)


class JudicialAuctionAnalyzer:
    """
    Enhanced analyzer for Brazilian judicial auction documents
    Provides comprehensive analysis of legal compliance and investment viability
    """
    
    def __init__(self):
        self.date_parser = DateParser()
        self.deadline_calculator = DeadlineCalculator()
        self.financial_analyzer = FinancialAnalyzer()
        self.compliance_checker = ComplianceChecker()
        self.property_analyzer = PropertyAnalyzer()
    
    def analyze(
        self, 
        text: str, 
        entities: Optional[Dict[str, List[str]]] = None,
        keywords: Optional[Dict[str, List[str]]] = None
    ) -> JudicialAnalysisResult:
        """
        Perform comprehensive judicial auction analysis
        
        Args:
            text: The document text to analyze
            entities: Pre-extracted entities (optional)
            keywords: Pre-extracted keywords (optional)
            
        Returns:
            JudicialAnalysisResult with all analysis components
        """
        logger.info("Starting judicial auction analysis")
        
        result = JudicialAnalysisResult()
        
        # Store raw data if provided
        if entities:
            result.raw_entities = entities
        if keywords:
            result.raw_keywords = keywords
        
        try:
            # 1.1 - Analyze auction type
            self._analyze_auction_type(text, result)
            
            # 1.2 - Analyze publication compliance
            self._analyze_publication_compliance(text, result)
            
            # 1.3 & 1.4 - Analyze CPC 889 notifications
            self._analyze_notifications(text, result)
            
            # 1.5 - Analyze valuation and auction values
            self._analyze_valuation(text, result)
            
            # 1.6 - Analyze debts
            self._analyze_debts(text, result)
            
            # 1.7 - Analyze property status
            self._analyze_property_status(text, result)
            
            # 1.8 - Analyze legal restrictions
            self._analyze_legal_restrictions(text, result)
            
            # Calculate overall scores and recommendations
            self._calculate_final_assessment(result)
            
        except Exception as e:
            logger.error(f"Error during judicial analysis: {e}")
            result.compliance_issues.append(f"Erro na análise: {str(e)}")
        
        return result
    
    def _analyze_auction_type(self, text: str, result: JudicialAnalysisResult) -> None:
        """Analyze whether auction is judicial or extrajudicial"""
        auction_analysis = self.compliance_checker.check_auction_type(text)
        
        if auction_analysis['auction_type'] == 'judicial':
            result.auction_type = AuctionType.JUDICIAL
        elif auction_analysis['auction_type'] == 'extrajudicial':
            result.auction_type = AuctionType.EXTRAJUDICIAL
        else:
            result.auction_type = AuctionType.UNKNOWN
        
        result.auction_type_confidence = auction_analysis['confidence']
        result.auction_type_indicators = (
            auction_analysis['judicial_indicators'] + 
            auction_analysis['extrajudicial_indicators']
        )
    
    def _analyze_publication_compliance(self, text: str, result: JudicialAnalysisResult) -> None:
        """Analyze publication compliance with legal requirements"""
        # Check publication mentions
        pub_check = self.compliance_checker.check_publication_compliance(text)
        
        result.publication_compliance.diario_oficial_mentioned = pub_check['diario_oficial_mentioned']
        result.publication_compliance.newspaper_mentioned = pub_check['newspaper_mentioned']
        result.publication_compliance.compliance_status = pub_check['compliance_status']
        result.publication_compliance.details = ' '.join(pub_check['compliance_notes'])
        
        # Extract dates
        pub_dates = self.date_parser.extract_publication_dates(text)
        auction_dates = self.date_parser.extract_auction_dates(text)
        
        result.publication_compliance.publication_dates = pub_dates
        result.publication_compliance.auction_dates = auction_dates
        
        # Check deadline compliance
        if pub_dates and auction_dates:
            deadline_analysis = self.deadline_calculator.analyze_deadline_compliance(
                pub_dates, auction_dates
            )
            
            if deadline_analysis['has_compliant_timeline']:
                result.publication_compliance.meets_deadline_requirement = True
                earliest = deadline_analysis['earliest_compliant_pair']
                result.publication_compliance.days_between_publication_auction = (
                    earliest['business_days']
                )
            else:
                result.publication_compliance.meets_deadline_requirement = False
                if deadline_analysis['min_days_found'] is not None:
                    result.publication_compliance.days_between_publication_auction = (
                        deadline_analysis['min_days_found']
                    )
                    result.compliance_issues.append(
                        f"Prazo insuficiente entre publicação e leilão "
                        f"({deadline_analysis['min_days_found']} dias úteis, mínimo 5)"
                    )
    
    def _analyze_notifications(self, text: str, result: JudicialAnalysisResult) -> None:
        """Analyze CPC Article 889 notification compliance"""
        cpc_analysis = self.compliance_checker.check_cpc_889_compliance(text)
        
        result.cpc_889_compliance = cpc_analysis['compliance_status']
        result.notification_analysis = ' '.join(cpc_analysis['compliance_notes'])
        
        # Create notification status for executado
        if 'I' in cpc_analysis['parties_notified']:
            result.executado_notification = NotificationStatus(
                party_type="Executado",
                notification_mentioned=True,
                compliance_status=ComplianceStatus.COMPLIANT,
                details=cpc_analysis['parties_notified']['I']
            )
        else:
            result.executado_notification = NotificationStatus(
                party_type="Executado",
                notification_mentioned=False,
                compliance_status=ComplianceStatus.NON_COMPLIANT,
                details="Notificação do executado não mencionada"
            )
            result.compliance_issues.append("Intimação do executado não confirmada (CPC 889, I)")
        
        # Create notification status for other parties
        for inciso, party in cpc_analysis['parties_notified'].items():
            if inciso != 'I':
                notification = NotificationStatus(
                    party_type=party,
                    notification_mentioned=True,
                    compliance_status=ComplianceStatus.COMPLIANT,
                    details=f"Inciso {inciso}"
                )
                result.other_notifications.append(notification)
        
        # Add missing notifications to compliance issues
        for missing in cpc_analysis['missing_notifications']:
            result.compliance_issues.append(f"Intimação não confirmada: {missing}")
    
    def _analyze_valuation(self, text: str, result: JudicialAnalysisResult) -> None:
        """Analyze property valuation and auction values"""
        # Extract auction values
        auction_values = self.financial_analyzer.extract_auction_values(text)
        
        result.valuation.market_value = auction_values.get('market_value')
        result.valuation.first_auction_value = auction_values.get('first_auction')
        result.valuation.second_auction_value = auction_values.get('second_auction')
        result.valuation.minimum_bid_value = auction_values.get('minimum_bid')
        
        # Store all found values
        for key, value in auction_values.items():
            if value is not None:
                result.valuation.values_found[key] = value
        
        # Analyze compliance
        compliance_analysis = self.financial_analyzer.analyze_valuation_compliance(auction_values)
        
        result.valuation.first_auction_percentage = compliance_analysis['first_auction_percentage']
        result.valuation.second_auction_percentage = compliance_analysis['second_auction_percentage']
        result.valuation.below_50_percent = compliance_analysis['below_50_percent']
        result.valuation.risk_of_annulment = compliance_analysis['risk_of_annulment']
        result.valuation.analysis_notes = ' '.join(compliance_analysis['analysis_notes'])
        
        if compliance_analysis['risk_of_annulment']:
            result.compliance_issues.append(
                "ALTO RISCO: Valor mínimo abaixo de 50% da avaliação - possível anulação"
            )
    
    def _analyze_debts(self, text: str, result: JudicialAnalysisResult) -> None:
        """Analyze existing debts and payment responsibility"""
        # Extract specific debts
        debts = self.financial_analyzer.extract_specific_debts(text)
        
        result.debts.iptu_debt = debts.get('iptu')
        result.debts.condominium_debt = debts.get('condominium')
        result.debts.mortgage_debt = debts.get('mortgage')
        
        # Store other debts
        for idx, value in enumerate(debts.get('other', [])):
            result.debts.other_debts[f'other_{idx+1}'] = value
        
        # Calculate total
        total = 0
        if result.debts.iptu_debt:
            total += result.debts.iptu_debt
            result.debts.debts_mentioned.append('IPTU')
        if result.debts.condominium_debt:
            total += result.debts.condominium_debt
            result.debts.debts_mentioned.append('Condomínio')
        if result.debts.mortgage_debt:
            total += result.debts.mortgage_debt
            result.debts.debts_mentioned.append('Hipoteca/Financiamento')
        
        total += sum(result.debts.other_debts.values())
        
        if total > 0:
            result.debts.total_debt = total
        
        # Analyze responsibility
        responsibility = self.financial_analyzer.analyze_debt_responsibility(text)
        result.debts.debt_responsibility = responsibility['debt_responsibility']
        
        if responsibility['debt_responsibility'] == 'arrematante':
            result.debts.analysis_notes = "Débitos por conta do arrematante"
            result.recommendations.append(
                "Verificar total de débitos antes da arrematação - serão de sua responsabilidade"
            )
        elif responsibility['debt_responsibility'] == 'quitado_com_lance':
            result.debts.analysis_notes = "Débitos serão quitados com o produto da arrematação"
        else:
            result.debts.analysis_notes = "Responsabilidade pelos débitos não está clara"
            result.compliance_issues.append(
                "Responsabilidade pelos débitos não especificada no edital"
            )
    
    def _analyze_property_status(self, text: str, result: JudicialAnalysisResult) -> None:
        """Analyze property occupation and status"""
        occupancy = self.property_analyzer.analyze_occupancy(text)
        
        result.property_status.occupancy_status = occupancy['occupancy_status']
        result.property_status.occupancy_details = occupancy['occupancy_details']
        result.property_status.has_tenants = occupancy['has_tenants']
        result.property_status.has_squatters = occupancy['has_squatters']
        result.property_status.has_disputes = occupancy['has_disputes']
        result.property_status.possession_transfer_risk = occupancy['possession_transfer_risk']
        result.property_status.risk_factors = occupancy['risk_factors']
        
        # Add recommendations based on occupancy
        if occupancy['occupancy_status'] == PropertyOccupancyStatus.VACANT:
            result.recommendations.append("Imóvel desocupado - facilita imissão na posse")
        elif occupancy['has_squatters']:
            result.recommendations.append(
                "ATENÇÃO: Possível ocupação irregular - consultar advogado sobre desocupação"
            )
        elif occupancy['has_tenants']:
            result.recommendations.append(
                "Imóvel ocupado - verificar contratos de locação e direitos do locatário"
            )
    
    def _analyze_legal_restrictions(self, text: str, result: JudicialAnalysisResult) -> None:
        """Analyze legal restrictions on the property"""
        restrictions = self.property_analyzer.analyze_legal_restrictions(text)
        
        result.legal_restrictions.has_judicial_unavailability = restrictions['has_judicial_unavailability']
        result.legal_restrictions.has_liens = restrictions['has_liens']
        result.legal_restrictions.has_mortgages = restrictions['has_mortgages']
        result.legal_restrictions.has_seizures = restrictions['has_seizures']
        result.legal_restrictions.restrictions_found = restrictions['restrictions_found']
        result.legal_restrictions.transfer_viability = restrictions['transfer_viability']
        result.legal_restrictions.restriction_details = restrictions['restriction_details']
        
        # Add compliance issues for serious restrictions
        if restrictions['has_judicial_unavailability']:
            result.compliance_issues.append(
                "CRÍTICO: Indisponibilidade judicial pode impedir transferência"
            )
        
        if restrictions['transfer_viability'] == 'blocked':
            result.recommendations.append(
                "NÃO ARREMATAR: Restrições impedem transferência do imóvel"
            )
        elif restrictions['transfer_viability'] == 'risky':
            result.recommendations.append(
                "Alto risco: Consultar advogado sobre viabilidade de resolver restrições"
            )
    
    def _calculate_final_assessment(self, result: JudicialAnalysisResult) -> None:
        """Calculate overall risk score and investment viability"""
        risk_score = 0
        viability_score = 50  # Start at neutral
        
        # Risk factors
        if result.auction_type == AuctionType.UNKNOWN:
            risk_score += 10
        
        if result.publication_compliance.compliance_status != ComplianceStatus.COMPLIANT:
            risk_score += 15
        
        if result.cpc_889_compliance != ComplianceStatus.COMPLIANT:
            risk_score += 20
        
        if result.valuation.risk_of_annulment:
            risk_score += 30
        
        if result.property_status.possession_transfer_risk == 'high':
            risk_score += 25
        elif result.property_status.possession_transfer_risk == 'medium':
            risk_score += 15
        
        if result.legal_restrictions.has_judicial_unavailability:
            risk_score += 40
        elif result.legal_restrictions.transfer_viability == 'risky':
            risk_score += 20
        
        # Positive factors
        if result.property_status.occupancy_status == PropertyOccupancyStatus.VACANT:
            viability_score += 20
        
        if result.debts.debt_responsibility == 'quitado_com_lance':
            viability_score += 10
        
        if result.legal_restrictions.transfer_viability == 'clear':
            viability_score += 15
        
        if result.valuation.second_auction_percentage:
            if 50 <= result.valuation.second_auction_percentage <= 70:
                viability_score += 15  # Good discount without annulment risk
        
        # Cap scores
        result.overall_risk_score = min(risk_score, 100)
        result.investment_viability_score = max(0, min(viability_score, 100))
        
        # Calculate confidence
        confidence_factors = []
        if result.auction_type != AuctionType.UNKNOWN:
            confidence_factors.append(result.auction_type_confidence)
        if result.publication_compliance.publication_dates:
            confidence_factors.append(0.8)
        if result.valuation.values_found:
            confidence_factors.append(0.9)
        
        if confidence_factors:
            result.confidence_level = sum(confidence_factors) / len(confidence_factors)
        else:
            result.confidence_level = 0.3
        
        # Final recommendations
        if result.overall_risk_score >= 70:
            result.recommendations.insert(0, 
                "⚠️ ALTO RISCO: Múltiplos problemas identificados - proceder com extrema cautela"
            )
        elif result.overall_risk_score >= 40:
            result.recommendations.insert(0,
                "⚠️ RISCO MODERADO: Alguns problemas identificados - análise cuidadosa recomendada"
            )
        
        if result.investment_viability_score >= 70:
            result.recommendations.insert(0,
                "✅ BOA OPORTUNIDADE: Indicadores favoráveis para investimento"
            )
        elif result.investment_viability_score <= 30:
            result.recommendations.insert(0,
                "❌ BAIXA VIABILIDADE: Muitos fatores negativos identificados"
            )