"""
Financial analysis for judicial auction documents
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

from .patterns import JudicialPatterns, JudicialKeywords

logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """Analyze financial aspects of judicial auctions"""
    
    def __init__(self):
        self.patterns = JudicialPatterns()
        self.keywords = JudicialKeywords()
    
    def parse_brazilian_currency(self, value_str: str) -> Optional[float]:
        """Convert Brazilian currency format to float"""
        try:
            # Remove R$ and spaces
            clean = value_str.replace('R$', '').strip()
            # Replace thousand separators and decimal comma
            clean = clean.replace('.', '').replace(',', '.')
            return float(clean)
        except (ValueError, AttributeError):
            return None
    
    def extract_monetary_values(self, text: str) -> List[Tuple[str, float]]:
        """Extract all monetary values from text"""
        values = []
        
        for match in self.patterns.FINANCIAL_PATTERNS['monetary'].finditer(text):
            value_str = match.group(0)
            value_float = self.parse_brazilian_currency(value_str)
            if value_float is not None:
                values.append((value_str, value_float))
        
        return values
    
    def extract_specific_debts(self, text: str) -> Dict[str, Optional[float]]:
        """Extract specific types of debts"""
        debts = {
            'iptu': None,
            'condominium': None,
            'mortgage': None,
            'other': []
        }
        
        # Extract IPTU
        iptu_pattern = re.compile(
            r'IPTU.*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        iptu_match = iptu_pattern.search(text)
        if iptu_match:
            debts['iptu'] = self.parse_brazilian_currency(iptu_match.group(0))
        
        # Extract condominium fees
        cond_pattern = re.compile(
            r'condom[íi]nio.*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        cond_match = cond_pattern.search(text)
        if cond_match:
            debts['condominium'] = self.parse_brazilian_currency(cond_match.group(0))
        
        # Extract mortgage/financing
        mortgage_pattern = re.compile(
            r'(?:hipoteca|financiamento|empr[ée]stimo).*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        mortgage_match = mortgage_pattern.search(text)
        if mortgage_match:
            debts['mortgage'] = self.parse_brazilian_currency(mortgage_match.group(0))
        
        # Look for other debts
        debt_pattern = re.compile(
            r'(?:d[ée]bito|d[íi]vida|pend[êe]ncia|inadimpl[êe]ncia).*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        for match in debt_pattern.finditer(text):
            value = self.parse_brazilian_currency(match.group(0))
            if value and value not in [debts['iptu'], debts['condominium'], debts['mortgage']]:
                debts['other'].append(value)
        
        return debts
    
    def extract_auction_values(self, text: str) -> Dict[str, Optional[float]]:
        """Extract auction-related values"""
        values = {
            'evaluation': None,
            'first_auction': None,
            'second_auction': None,
            'minimum_bid': None,
            'market_value': None
        }
        
        # Extract evaluation value
        eval_pattern = re.compile(
            r'avalia[çc][ãa]o.*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        eval_match = eval_pattern.search(text)
        if eval_match:
            values['evaluation'] = self.parse_brazilian_currency(eval_match.group(0))
        
        # Extract first auction value
        first_pattern = re.compile(
            r'(?:primeira\s*pra[çc]a|1[ªa]\s*pra[çc]a).*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        first_match = first_pattern.search(text)
        if first_match:
            values['first_auction'] = self.parse_brazilian_currency(first_match.group(0))
        
        # Extract second auction value
        second_pattern = re.compile(
            r'(?:segunda\s*pra[çc]a|2[ªa]\s*pra[çc]a).*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        second_match = second_pattern.search(text)
        if second_match:
            values['second_auction'] = self.parse_brazilian_currency(second_match.group(0))
        
        # Extract minimum bid
        min_pattern = re.compile(
            r'(?:lance\s*m[íi]nimo|valor\s*m[íi]nimo).*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        min_match = min_pattern.search(text)
        if min_match:
            values['minimum_bid'] = self.parse_brazilian_currency(min_match.group(0))
        
        # Extract market value
        market_pattern = re.compile(
            r'(?:valor\s*de\s*mercado|valor\s*venal).*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        )
        market_match = market_pattern.search(text)
        if market_match:
            values['market_value'] = self.parse_brazilian_currency(market_match.group(0))
        
        return values
    
    def analyze_valuation_compliance(self, auction_values: Dict[str, Optional[float]]) -> Dict[str, any]:
        """Analyze if auction values comply with legal requirements"""
        analysis = {
            'has_evaluation': False,
            'first_auction_percentage': None,
            'second_auction_percentage': None,
            'below_50_percent': False,
            'risk_of_annulment': False,
            'analysis_notes': []
        }
        
        eval_value = auction_values.get('evaluation') or auction_values.get('market_value')
        
        if not eval_value:
            analysis['analysis_notes'].append("Valor de avaliação não encontrado")
            return analysis
        
        analysis['has_evaluation'] = True
        
        # Check first auction value (usually should be 100% of evaluation)
        if auction_values.get('first_auction'):
            percentage = (auction_values['first_auction'] / eval_value) * 100
            analysis['first_auction_percentage'] = percentage
            
            if percentage < 100:
                analysis['analysis_notes'].append(
                    f"1ª praça abaixo da avaliação ({percentage:.1f}%)"
                )
        
        # Check second auction value (cannot be below 50% in many cases)
        if auction_values.get('second_auction'):
            percentage = (auction_values['second_auction'] / eval_value) * 100
            analysis['second_auction_percentage'] = percentage
            
            if percentage < 50:
                analysis['below_50_percent'] = True
                analysis['risk_of_annulment'] = True
                analysis['analysis_notes'].append(
                    f"2ª praça abaixo de 50% da avaliação ({percentage:.1f}%) - RISCO DE ANULAÇÃO"
                )
            elif percentage < 60:
                analysis['analysis_notes'].append(
                    f"2ª praça próxima ao limite mínimo ({percentage:.1f}%)"
                )
        
        # Check minimum bid if no auction values
        if not auction_values.get('first_auction') and not auction_values.get('second_auction'):
            if auction_values.get('minimum_bid'):
                percentage = (auction_values['minimum_bid'] / eval_value) * 100
                if percentage < 50:
                    analysis['below_50_percent'] = True
                    analysis['risk_of_annulment'] = True
                    analysis['analysis_notes'].append(
                        f"Lance mínimo abaixo de 50% ({percentage:.1f}%) - RISCO DE ANULAÇÃO"
                    )
        
        return analysis
    
    def analyze_debt_responsibility(self, text: str) -> Dict[str, any]:
        """Analyze who is responsible for existing debts"""
        analysis = {
            'debt_responsibility': 'unknown',
            'specific_mentions': [],
            'confidence': 0.0
        }
        
        # Patterns indicating arrematante responsibility
        arrematante_patterns = [
            r'responsabilidade\s+do\s+arrematante',
            r'[ôo]nus\s+do\s+arrematante',
            r'arrematante\s+(?:arcar[áa]|assumir[áa]|responder[áa])',
            r'd[ée]bitos?\s+(?:por\s+conta|a\s+cargo)\s+do\s+arrematante'
        ]
        
        # Patterns indicating debts paid with auction proceeds
        quitado_patterns = [
            r'sub-?roga[çc][ãa]o',
            r'quitad[oa]s?\s+com\s+o\s+produto',
            r'pag[oa]s?\s+com\s+o\s+valor\s+da\s+arremata[çc][ãa]o',
            r'livre\s+de\s+d[ée]bitos?',
            r'd[ée]bitos?\s+(?:ser[ãa]o\s+)?quitad[oa]s?'
        ]
        
        # Check for arrematante responsibility
        for pattern in arrematante_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                analysis['debt_responsibility'] = 'arrematante'
                analysis['specific_mentions'].append(pattern)
                analysis['confidence'] = 0.8
                break
        
        # Check for debts paid with proceeds
        if analysis['debt_responsibility'] == 'unknown':
            for pattern in quitado_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    analysis['debt_responsibility'] = 'quitado_com_lance'
                    analysis['specific_mentions'].append(pattern)
                    analysis['confidence'] = 0.8
                    break
        
        # Look for specific debt mentions
        if 'IPTU' in text.upper():
            iptu_resp = self._check_specific_debt_responsibility(text, 'IPTU')
            if iptu_resp:
                analysis['specific_mentions'].append(f"IPTU: {iptu_resp}")
        
        if re.search(r'condom[íi]nio', text, re.IGNORECASE):
            cond_resp = self._check_specific_debt_responsibility(text, 'condomínio')
            if cond_resp:
                analysis['specific_mentions'].append(f"Condomínio: {cond_resp}")
        
        return analysis
    
    def _check_specific_debt_responsibility(self, text: str, debt_type: str) -> Optional[str]:
        """Check responsibility for a specific type of debt"""
        # Create a window around the debt mention
        pattern = re.compile(
            f'{debt_type}.*?(?:responsabilidade|cargo|conta|assumid[oa]|arcar|pag[oa])',
            re.IGNORECASE | re.DOTALL
        )
        
        match = pattern.search(text)
        if match:
            context = match.group(0)
            if re.search(r'arrematante', context, re.IGNORECASE):
                return "responsabilidade do arrematante"
            elif re.search(r'(?:quit|pag|sub-?rog)', context, re.IGNORECASE):
                return "será quitado"
        
        return None