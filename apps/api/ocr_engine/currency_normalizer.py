"""
Currency Normalizer - Week 2 Implementation
Specialized currency and numerical value normalization for Brazilian legal documents
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import locale

logger = logging.getLogger(__name__)

@dataclass
class CurrencyNormalizationResult:
    """Result of currency normalization process"""
    original_text: str
    normalized_text: str
    currency_values: List[Dict[str, any]]
    normalizations: List[Dict[str, str]]
    confidence_score: float
    processing_time: float

class CurrencyNormalizer:
    """
    Brazilian currency and number normalization for legal documents
    Handles R$ formats, number formats, and legal value patterns
    """
    
    def __init__(self):
        """Initialize with Brazilian currency patterns and formats"""
        self.currency_patterns = self._build_currency_patterns()
        self.number_patterns = self._build_number_patterns()
        self.legal_value_patterns = self._build_legal_value_patterns()
        self.date_patterns = self._build_date_patterns()
        
        # Try to set Brazilian locale for number formatting
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
            except locale.Error:
                logger.warning("Could not set Brazilian locale for number formatting")
        
        logger.info("Currency Normalizer initialized with Brazilian formats")
    
    def _build_currency_patterns(self) -> Dict[str, str]:
        """Build currency normalization patterns"""
        return {
            # Fix R$ variations
            r'R\$?\s*(\d{1,3}(?:\.\d{3})*),(\d{2})': r'R$ \1,\2',  # R$ 1.000,00
            r'R\$?\s*(\d{1,3}(?:\.\d{3})*),(\d{1})(?!\d)': r'R$ \1,\g<2>0',  # R$ 1.000,5 → R$ 1.000,50
            r'R\$?\s*(\d+)\.(\d{2})(?!\d)': r'R$ \1,\2',  # R$ 1000.50 → R$ 1000,50
            r'R\$?\s*(\d+),(\d{3})(?:\.|,)(\d{2})': r'R$ \1.\2,\3',  # Fix mixed separators
            
            # Currency without R$ symbol
            r'(\d{1,3}(?:\.\d{3})*),(\d{2})\s*reais?': r'R$ \1,\2',
            r'(\d+)\s*mil\s*reais?': self._convert_mil_reais,
            r'(\d+)\s*milh[õo]es?\s*de\s*reais?': self._convert_milhoes_reais,
            
            # Fix common OCR errors in currency
            r'R5\s*(\d)': r'R$ \1',
            r'R8\s*(\d)': r'R$ \1', 
            r'R§\s*(\d)': r'R$ \1',
            r'RS\s*(\d)': r'R$ \1',
            r'R\$\s*O(\d)': r'R$ 0\1',  # R$ O123 → R$ 0123
            
            # Standardize spacing
            r'R\$(\d)': r'R$ \1',  # R$123 → R$ 123
            r'R\$\s{2,}': 'R$ ',   # Multiple spaces to single space
        }
    
    def _build_number_patterns(self) -> Dict[str, str]:
        """Build number normalization patterns"""
        return {
            # Brazilian number format standardization
            r'(\d{1,3})\.(\d{3})\.(\d{3}),(\d{2})': r'\1.\2.\3,\4',  # Already correct
            r'(\d{1,3})\.(\d{3}),(\d{2})': r'\1.\2,\3',              # Already correct
            r'(\d+),(\d{2})': r'\1,\2',                              # Already correct
            
            # Fix common separators
            r'(\d+)\.(\d{2})(?!\d)': r'\1,\2',  # 1000.50 → 1000,50 (decimal)
            r'(\d{1,3})\.(\d{3})\.(\d{3})\.(\d{2})': r'\1.\2.\3,\4',  # Fix extra dot
            
            # Percentage normalization
            r'(\d+),(\d+)\s*%': r'\1,\2%',      # 10,5 % → 10,5%
            r'(\d+)\s*%': r'\1%',               # 10 % → 10%
            r'(\d+),(\d+)por\s*cento': r'\1,\2%',  # 10,5por cento → 10,5%
            r'(\d+)\s*por\s*cento': r'\1%',     # 10 por cento → 10%
            
            # Fix OCR digit errors in numbers
            r'(\d+)O(\d+)': r'\g<1>0\2',       # 1O23 → 1023
            r'(\d+)l(\d+)': r'\g<1>1\2',       # 1l23 → 1123
            r'(\d+)S(\d+)': r'\g<1>5\2',       # 1S23 → 1523
        }
    
    def _build_legal_value_patterns(self) -> Dict[str, str]:
        """Build legal value pattern normalization"""
        return {
            # Auction values
            r'lance\s*m[íi]nimo.*?R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})': 
                r'lance mínimo: R$ \1,\2',
            r'valor\s*da?\s*avalia[çc][ãa]o.*?R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})':
                r'valor da avaliação: R$ \1,\2',
            r'd[ée]bito\s*total.*?R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})':
                r'débito total: R$ \1,\2',
            
            # Property values
            r'iptu.*?R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})':
                r'IPTU: R$ \1,\2',
            r'condom[íi]nio.*?R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})':
                r'condomínio: R$ \1,\2',
            r'itbi.*?R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})':
                r'ITBI: R$ \1,\2',
            
            # Legal costs
            r'honor[áa]rios.*?R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})':
                r'honorários: R$ \1,\2',
            r'custas.*?R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})':
                r'custas: R$ \1,\2',
            
            # Fractional values (common in auctions)
            r'(\d+)/(\d+)\s*do\s*valor': r'\1/\2 do valor',  # 2/3 do valor
            r'dois\s*ter[çc]os': '2/3',
            r'tr[êe]s\s*quartos': '3/4',
            r'metade': '1/2',
        }
    
    def _build_date_patterns(self) -> Dict[str, str]:
        """Build date pattern normalization"""
        return {
            # Brazilian date format: DD/MM/YYYY
            r'(\d{1,2})/(\d{1,2})/(\d{4})': r'\1/\2/\3',  # Already correct
            r'(\d{1,2})-(\d{1,2})-(\d{4})': r'\1/\2/\3',  # DD-MM-YYYY → DD/MM/YYYY
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})': r'\1/\2/\3',  # DD.MM.YYYY → DD/MM/YYYY
            
            # Month names
            r'(\d{1,2})\s*de\s*janeiro\s*de\s*(\d{4})': r'\1/01/\2',
            r'(\d{1,2})\s*de\s*fevereiro\s*de\s*(\d{4})': r'\1/02/\2',
            r'(\d{1,2})\s*de\s*mar[çc]o\s*de\s*(\d{4})': r'\1/03/\2',
            r'(\d{1,2})\s*de\s*abril\s*de\s*(\d{4})': r'\1/04/\2',
            r'(\d{1,2})\s*de\s*maio\s*de\s*(\d{4})': r'\1/05/\2',
            r'(\d{1,2})\s*de\s*junho\s*de\s*(\d{4})': r'\1/06/\2',
            r'(\d{1,2})\s*de\s*julho\s*de\s*(\d{4})': r'\1/07/\2',
            r'(\d{1,2})\s*de\s*agosto\s*de\s*(\d{4})': r'\1/08/\2',
            r'(\d{1,2})\s*de\s*setembro\s*de\s*(\d{4})': r'\1/09/\2',
            r'(\d{1,2})\s*de\s*outubro\s*de\s*(\d{4})': r'\1/10/\2',
            r'(\d{1,2})\s*de\s*novembro\s*de\s*(\d{4})': r'\1/11/\2',
            r'(\d{1,2})\s*de\s*dezembro\s*de\s*(\d{4})': r'\1/12/\2',
            
            # Time format
            r'(\d{1,2})[h:](\d{2})\s*h?o?r?a?s?': r'\1h\2',
            r'as\s*(\d{1,2})[h:](\d{2})': r'às \1h\2',
        }
    
    def _convert_mil_reais(self, match) -> str:
        """Convert 'X mil reais' to R$ format"""
        value = int(match.group(1))
        return f'R$ {value:,}'.replace(',', '.')
    
    def _convert_milhoes_reais(self, match) -> str:
        """Convert 'X milhões de reais' to R$ format"""
        value = int(match.group(1)) * 1000000
        return f'R$ {value:,}'.replace(',', '.')
    
    def normalize_currency(self, text: str) -> CurrencyNormalizationResult:
        """
        Normalize currency and numerical values in text
        
        Args:
            text: Raw text to normalize
            
        Returns:
            CurrencyNormalizationResult with normalized text and metadata
        """
        start_time = datetime.now()
        original_text = text
        normalizations = []
        currency_values = []
        
        try:
            # Step 1: Currency pattern normalization
            text, currency_norms = self._apply_currency_patterns(text)
            normalizations.extend(currency_norms)
            
            # Step 2: Number pattern normalization
            text, number_norms = self._apply_number_patterns(text)
            normalizations.extend(number_norms)
            
            # Step 3: Legal value pattern normalization
            text, legal_norms = self._apply_legal_value_patterns(text)
            normalizations.extend(legal_norms)
            
            # Step 4: Date pattern normalization
            text, date_norms = self._apply_date_patterns(text)
            normalizations.extend(date_norms)
            
            # Step 5: Extract normalized currency values
            currency_values = self._extract_currency_values(text)
            
            # Step 6: Final validation
            text = self._final_currency_validation(text)
            
            # Calculate confidence score
            confidence_score = self._calculate_normalization_confidence(
                original_text, text, normalizations, currency_values
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Currency normalization completed: {len(normalizations)} normalizations, "
                       f"{len(currency_values)} currency values found")
            
            return CurrencyNormalizationResult(
                original_text=original_text,
                normalized_text=text,
                currency_values=currency_values,
                normalizations=normalizations,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in currency normalization: {e}")
            return CurrencyNormalizationResult(
                original_text=original_text,
                normalized_text=original_text,
                currency_values=[],
                normalizations=[],
                confidence_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _apply_currency_patterns(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply currency normalization patterns"""
        normalizations = []
        normalized_text = text
        
        for pattern, replacement in self.currency_patterns.items():
            if callable(replacement):
                # Handle callable replacements
                matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
                for match in matches:
                    old_text = match.group()
                    new_text = replacement(match)
                    
                    if new_text != old_text:
                        normalizations.append({
                            'type': 'currency_conversion',
                            'from': old_text,
                            'to': new_text,
                            'pattern': pattern
                        })
                        normalized_text = normalized_text.replace(old_text, new_text)
            else:
                # Handle string replacements
                matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
                
                for match in matches:
                    old_text = match.group()
                    new_text = re.sub(pattern, replacement, old_text, flags=re.IGNORECASE)
                    
                    if new_text != old_text:
                        normalizations.append({
                            'type': 'currency_pattern',
                            'from': old_text,
                            'to': new_text,
                            'pattern': pattern
                        })
                
                normalized_text = re.sub(pattern, replacement, normalized_text, flags=re.IGNORECASE)
        
        return normalized_text, normalizations
    
    def _apply_number_patterns(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply number normalization patterns"""
        normalizations = []
        normalized_text = text
        
        for pattern, replacement in self.number_patterns.items():
            matches = re.finditer(pattern, normalized_text)
            
            for match in matches:
                old_text = match.group()
                new_text = re.sub(pattern, replacement, old_text)
                
                if new_text != old_text:
                    normalizations.append({
                        'type': 'number_pattern',
                        'from': old_text,
                        'to': new_text,
                        'category': self._get_number_category(old_text)
                    })
            
            normalized_text = re.sub(pattern, replacement, normalized_text)
        
        return normalized_text, normalizations
    
    def _apply_legal_value_patterns(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply legal value pattern normalization"""
        normalizations = []
        normalized_text = text
        
        for pattern, replacement in self.legal_value_patterns.items():
            matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
            
            for match in matches:
                old_text = match.group()
                new_text = re.sub(pattern, replacement, old_text, flags=re.IGNORECASE)
                
                if new_text != old_text:
                    normalizations.append({
                        'type': 'legal_value',
                        'from': old_text,
                        'to': new_text,
                        'category': self._get_legal_value_category(new_text)
                    })
            
            normalized_text = re.sub(pattern, replacement, normalized_text, flags=re.IGNORECASE)
        
        return normalized_text, normalizations
    
    def _apply_date_patterns(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply date normalization patterns"""
        normalizations = []
        normalized_text = text
        
        for pattern, replacement in self.date_patterns.items():
            matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
            
            for match in matches:
                old_text = match.group()
                new_text = re.sub(pattern, replacement, old_text, flags=re.IGNORECASE)
                
                if new_text != old_text:
                    normalizations.append({
                        'type': 'date_pattern',
                        'from': old_text,
                        'to': new_text,
                        'category': 'temporal'
                    })
            
            normalized_text = re.sub(pattern, replacement, normalized_text, flags=re.IGNORECASE)
        
        return normalized_text, normalizations
    
    def _extract_currency_values(self, text: str) -> List[Dict[str, any]]:
        """Extract and parse all currency values from text"""
        currency_values = []
        
        # Main R$ pattern
        pattern = r'R\$\s*(\d{1,3}(?:\.\d{3})*),(\d{2})'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            try:
                # Convert Brazilian format to float
                amount_str = f"{match.group(1)},{match.group(2)}"
                amount_float = float(amount_str.replace('.', '').replace(',', '.'))
                
                currency_values.append({
                    'raw_text': match.group(),
                    'formatted_value': f"R$ {match.group(1)},{match.group(2)}",
                    'numeric_value': amount_float,
                    'position': match.start(),
                    'currency': 'BRL'
                })
                
            except ValueError:
                logger.warning(f"Could not parse currency value: {match.group()}")
        
        # Sort by value for analysis
        currency_values.sort(key=lambda x: x['numeric_value'], reverse=True)
        
        return currency_values
    
    def _final_currency_validation(self, text: str) -> str:
        """Final validation and cleanup for currency text"""
        
        # Ensure proper R$ spacing
        text = re.sub(r'R\$\s*(\d)', r'R$ \1', text)
        
        # Fix common currency OCR errors
        text = re.sub(r'R\$\s*O(\d)', r'R$ 0\1', text)
        text = re.sub(r'R\$\s*l(\d)', r'R$ 1\1', text)
        
        # Standardize currency context
        text = re.sub(r'reais?', 'reais', text, flags=re.IGNORECASE)
        
        # Ensure proper formatting for legal amounts
        text = re.sub(r'(R\$\s*\d{1,3}(?:\.\d{3})*,\d{2})\s*\([^)]+\)', r'\1', text)
        
        return text
    
    def _get_number_category(self, number_text: str) -> str:
        """Get category for number normalization"""
        if '%' in number_text:
            return 'percentage'
        elif ',' in number_text or '.' in number_text:
            return 'decimal'
        else:
            return 'integer'
    
    def _get_legal_value_category(self, value_text: str) -> str:
        """Get category for legal value"""
        categories = {
            'auction': ['lance', 'avaliação', 'arrematação'],
            'debt': ['débito', 'dívida', 'pendência'],
            'tax': ['iptu', 'itbi', 'taxa'],
            'cost': ['honorários', 'custas', 'despesa'],
            'property': ['condomínio', 'valor', 'preço']
        }
        
        value_lower = value_text.lower()
        for category, terms in categories.items():
            if any(term in value_lower for term in terms):
                return category
        
        return 'general'
    
    def _calculate_normalization_confidence(self, original: str, normalized: str,
                                          normalizations: List[Dict], 
                                          currency_values: List[Dict]) -> float:
        """Calculate confidence score for normalization"""
        
        if not original:
            return 0.0
        
        # Base confidence
        base_confidence = 0.90
        
        # Factor in currency values found
        currency_bonus = min(0.05, len(currency_values) * 0.01)
        
        # Factor in normalization quality
        if normalizations:
            normalization_density = len(normalizations) / len(original.split())
            if normalization_density > 0.2:  # Too many changes
                confidence_penalty = 0.1
            else:
                confidence_penalty = 0.0
        else:
            confidence_penalty = 0.0
        
        # Factor in proper Brazilian formatting
        br_format_matches = len(re.findall(r'R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}', normalized))
        format_bonus = min(0.05, br_format_matches * 0.01)
        
        final_confidence = base_confidence + currency_bonus + format_bonus - confidence_penalty
        return max(0.0, min(1.0, final_confidence))

# Global normalizer instance
currency_normalizer = CurrencyNormalizer()

def normalize_currency_text(text: str) -> CurrencyNormalizationResult:
    """
    Convenience function for currency normalization
    
    Args:
        text: Raw text to normalize
        
    Returns:
        CurrencyNormalizationResult with normalized text and metadata
    """
    return currency_normalizer.normalize_currency(text)