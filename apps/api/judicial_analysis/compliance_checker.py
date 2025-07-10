"""
Legal compliance checking for judicial auctions
"""

import re
from typing import Dict, List, Optional, Set
import logging

from .patterns import JudicialPatterns, JudicialKeywords
from .models import ComplianceStatus, NotificationStatus

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Check legal compliance requirements for judicial auctions"""
    
    def __init__(self):
        self.patterns = JudicialPatterns()
        self.keywords = JudicialKeywords()
    
    def check_cpc_889_compliance(self, text: str) -> Dict[str, any]:
        """Check compliance with CPC Article 889 notification requirements"""
        result = {
            'article_mentioned': False,
            'parties_notified': {},
            'notification_methods': [],
            'compliance_status': ComplianceStatus.CANNOT_DETERMINE,
            'missing_notifications': [],
            'compliance_notes': []
        }
        
        # Check if Article 889 is mentioned
        if self.patterns.CPC_889_PATTERNS['article_mention'].search(text):
            result['article_mentioned'] = True
            result['compliance_notes'].append("Artigo 889 do CPC mencionado")
        
        # Extract notification verbs and methods
        notification_verbs = self.patterns.CPC_889_PATTERNS['notification_verb'].findall(text)
        result['notification_methods'] = list(set(notification_verbs))
        
        # Check each required party type
        for inciso, party_types in self.keywords.NOTIFICATION_KEYWORDS['cpc_889_parties'].items():
            for party_type in party_types:
                if self._check_party_notification(text, party_type):
                    result['parties_notified'][inciso] = party_type
                    break
        
        # Analyze compliance
        notified_count = len(result['parties_notified'])
        
        if notified_count >= 4:  # Most important parties notified
            result['compliance_status'] = ComplianceStatus.COMPLIANT
        elif notified_count >= 2:  # Some parties notified
            result['compliance_status'] = ComplianceStatus.PARTIALLY_COMPLIANT
        elif notified_count > 0:  # Few parties notified
            result['compliance_status'] = ComplianceStatus.NON_COMPLIANT
        
        # Identify missing critical notifications
        critical_parties = ['I', 'II', 'V']  # Executado, Cônjuge, Credor Hipotecário
        for inciso in critical_parties:
            if inciso not in result['parties_notified']:
                party_name = list(self.keywords.NOTIFICATION_KEYWORDS['cpc_889_parties'][inciso])[0]
                result['missing_notifications'].append(f"{inciso} - {party_name}")
        
        return result
    
    def _check_party_notification(self, text: str, party_type: str) -> bool:
        """Check if a specific party type was notified"""
        # Create search window around party mention
        party_pattern = re.compile(
            f'{party_type}.*?(?:intimad|notificad|citad|cientificad)',
            re.IGNORECASE | re.DOTALL
        )
        
        # Also check reverse order
        notification_pattern = re.compile(
            f'(?:intimad|notificad|citad|cientificad).*?{party_type}',
            re.IGNORECASE | re.DOTALL
        )
        
        return bool(party_pattern.search(text) or notification_pattern.search(text))
    
    def check_publication_compliance(self, text: str) -> Dict[str, any]:
        """Check if publication requirements were met"""
        result = {
            'diario_oficial_mentioned': False,
            'newspaper_mentioned': False,
            'publication_keywords': [],
            'compliance_status': ComplianceStatus.CANNOT_DETERMINE,
            'compliance_notes': []
        }
        
        # Check for Diário Oficial
        for keyword in self.keywords.PUBLICATION_COMPLIANCE['official_gazette']:
            if keyword.lower() in text.lower():
                result['diario_oficial_mentioned'] = True
                result['publication_keywords'].append(keyword)
                break
        
        # Check for newspaper
        for keyword in self.keywords.PUBLICATION_COMPLIANCE['newspaper']:
            if keyword.lower() in text.lower():
                result['newspaper_mentioned'] = True
                result['publication_keywords'].append(keyword)
                break
        
        # Check for publication verbs
        pub_verbs = ['publicado', 'publicada', 'publicação', 'divulgado', 'divulgação']
        found_verbs = [v for v in pub_verbs if v in text.lower()]
        result['publication_keywords'].extend(found_verbs)
        
        # Analyze compliance
        if result['diario_oficial_mentioned'] and result['newspaper_mentioned']:
            result['compliance_status'] = ComplianceStatus.COMPLIANT
            result['compliance_notes'].append("Publicação em Diário Oficial e jornal mencionadas")
        elif result['diario_oficial_mentioned'] or result['newspaper_mentioned']:
            result['compliance_status'] = ComplianceStatus.PARTIALLY_COMPLIANT
            result['compliance_notes'].append("Apenas uma forma de publicação mencionada")
        elif found_verbs:
            result['compliance_status'] = ComplianceStatus.PARTIALLY_COMPLIANT
            result['compliance_notes'].append("Publicação mencionada sem especificar veículo")
        
        return result
    
    def extract_process_details(self, text: str) -> Dict[str, any]:
        """Extract judicial process details for verification"""
        details = {
            'process_numbers': [],
            'court_mentions': [],
            'judge_mentions': [],
            'auctioneer_mentions': [],
            'legal_basis': []
        }
        
        # Extract process numbers
        process_pattern = re.compile(r'\d{7}-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')
        details['process_numbers'] = process_pattern.findall(text)
        
        # Extract court mentions
        court_pattern = re.compile(
            r'(?:\d+[ªa]?\s*)?vara\s+(?:c[íi]vel|empresarial|fam[íi]lia|faz|federal)',
            re.IGNORECASE
        )
        details['court_mentions'] = court_pattern.findall(text)
        
        # Extract judge names (pattern for Brazilian names)
        judge_pattern = re.compile(
            r'(?:ju[íi]z[ae]?|magistrad[oa]|mm\.?|meritíssim[oa])\s+'
            r'(?:dr[ae]?\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            re.IGNORECASE
        )
        for match in judge_pattern.finditer(text):
            details['judge_mentions'].append(match.group(1))
        
        # Extract auctioneer information
        auctioneer_pattern = re.compile(
            r'leiloeiro\s+(?:oficial\s+)?(?:p[úu]blico\s+)?'
            r'(?:dr[ae]?\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            re.IGNORECASE
        )
        for match in auctioneer_pattern.finditer(text):
            details['auctioneer_mentions'].append(match.group(1))
        
        # Extract legal basis
        legal_patterns = [
            r'lei\s+n[º°]?\s*[\d\.\/\-]+',
            r'artigo\s+\d+',
            r'CPC.*?\d+',
            r'c[óo]digo\s+de\s+processo\s+civil',
            r'lei\s+de\s+execu[çc][ãa]o\s+fiscal'
        ]
        
        for pattern in legal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            details['legal_basis'].extend(matches)
        
        return details
    
    def check_auction_type(self, text: str) -> Dict[str, any]:
        """Determine if auction is judicial or extrajudicial"""
        result = {
            'auction_type': 'unknown',
            'confidence': 0.0,
            'judicial_indicators': [],
            'extrajudicial_indicators': []
        }
        
        # Count indicators
        text_lower = text.lower()
        
        for indicator in self.keywords.AUCTION_TYPE['judicial']:
            if indicator in text_lower:
                result['judicial_indicators'].append(indicator)
        
        for indicator in self.keywords.AUCTION_TYPE['extrajudicial']:
            if indicator in text_lower:
                result['extrajudicial_indicators'].append(indicator)
        
        # Determine type based on indicators
        judicial_score = len(result['judicial_indicators'])
        extrajudicial_score = len(result['extrajudicial_indicators'])
        
        if judicial_score > extrajudicial_score:
            result['auction_type'] = 'judicial'
            if judicial_score >= 5:
                result['confidence'] = 0.9
            elif judicial_score >= 3:
                result['confidence'] = 0.7
            else:
                result['confidence'] = 0.5
        elif extrajudicial_score > judicial_score:
            result['auction_type'] = 'extrajudicial'
            if extrajudicial_score >= 3:
                result['confidence'] = 0.8
            else:
                result['confidence'] = 0.6
        elif judicial_score > 0:  # Equal but non-zero
            result['auction_type'] = 'judicial'  # Default to judicial
            result['confidence'] = 0.4
        
        return result