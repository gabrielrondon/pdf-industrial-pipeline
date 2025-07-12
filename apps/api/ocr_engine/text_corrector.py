"""
OCR Text Corrector - Week 2 Implementation
Intelligent error correction for OCR text with focus on Brazilian legal documents
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class CorrectionResult:
    """Result of text correction process"""
    original_text: str
    corrected_text: str
    corrections_made: List[Dict[str, str]]
    confidence_score: float
    processing_time: float
    
    def to_dict(self) -> Dict:
        return {
            'original_text': self.original_text,
            'corrected_text': self.corrected_text,
            'corrections_made': self.corrections_made,
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time
        }

class OCRTextCorrector:
    """
    Advanced OCR text correction focused on Brazilian legal documents
    Implements zero-cost improvements using pattern recognition and domain knowledge
    """
    
    def __init__(self):
        """Initialize with Brazilian legal domain correction patterns"""
        self.character_corrections = self._build_character_corrections()
        self.word_corrections = self._build_word_corrections()
        self.legal_patterns = self._build_legal_patterns()
        self.spacing_patterns = self._build_spacing_patterns()
        
        logger.info("OCR Text Corrector initialized with Brazilian legal domain knowledge")
    
    def _build_character_corrections(self) -> Dict[str, str]:
        """Build character-level correction mappings"""
        return {
            # Common OCR character errors
            'rn': 'm',      # rn → m (common in OCR)
            'vv': 'w',      # vv → w
            '0': 'O',       # 0 → O (in words, not numbers)
            '1': 'l',       # 1 → l (in words)
            '8': 'B',       # 8 → B (in some contexts)
            '6': 'G',       # 6 → G (in some contexts)
            '5': 'S',       # 5 → S (in some contexts)
            
            # Portuguese specific corrections
            'ã': 'ã',       # Normalize tilde
            'ç': 'ç',       # Normalize cedilla
            'õ': 'õ',       # Normalize tilde
            
            # Legal document specific
            '§': '§',       # Paragraph symbol
            'º': 'º',       # Ordinal indicator
            'ª': 'ª',       # Feminine ordinal
            '°': 'º',       # Degree to ordinal
        }
    
    def _build_word_corrections(self) -> Dict[str, str]:
        """Build word-level correction mappings for legal terms"""
        return {
            # Common legal term OCR errors
            'leil5o': 'leilão',
            'leil50': 'leilão',
            'leilao': 'leilão',
            'execu§ao': 'execução',
            'execuc5o': 'execução',
            'execucao': 'execução',
            'avalia§ao': 'avaliação',
            'avaliac5o': 'avaliação',
            'avaliacao': 'avaliação',
            'cita§ao': 'citação',
            'citac5o': 'citação',
            'citacao': 'citação',
            'intima§ao': 'intimação',
            'intimac5o': 'intimação',
            'intimacao': 'intimação',
            'peti§ao': 'petição',
            'peticao': 'petição',
            'deci5ao': 'decisão',
            'decisao': 'decisão',
            'sen§a': 'sentença',
            'sentenca': 'sentença',
            'senten§a': 'sentença',
            
            # Court terms
            'tribuna1': 'tribunal',
            'tribunaI': 'tribunal',
            'ju1zo': 'juízo',
            'juizo': 'juízo',
            'juiZo': 'juízo',
            'c0marca': 'comarca',
            'comarcã': 'comarca',
            
            # Process terms
            'pr0cesso': 'processo',
            'processo': 'processo',
            'proc3sso': 'processo',
            'a§ao': 'ação',
            'acao': 'ação',
            '5§ao': 'ção',  # Common suffix error
            
            # Property terms
            'im0vel': 'imóvel',
            'imovel': 'imóvel',
            'im6vel': 'imóvel',
            'ap5rtamento': 'apartamento',
            'apartament0': 'apartamento',
            'edifici0': 'edifício',
            'edificio': 'edifício',
            
            # Financial terms
            'R5': 'R$',
            'R8': 'R$',
            'R§': 'R$',
            'rea1s': 'reais',
            'reais': 'reais',
            'mi1': 'mil',
            'mi1hao': 'milhão',
            'milhao': 'milhão',
            
            # Dates and numbers
            'marc0': 'março',
            'abri1': 'abril',
            'ju1ho': 'julho',
            'agost0': 'agosto',
            'setembro': 'setembro',
            '0utubro': 'outubro',
            'n0vembro': 'novembro',
            'dezembro': 'dezembro'
        }
    
    def _build_legal_patterns(self) -> Dict[str, str]:
        """Build legal pattern corrections"""
        return {
            # Process number patterns (Brazilian format: 1234567-89.2023.8.26.0100)
            r'(\d{7})-?(\d{2})\.?(\d{4})\.?(\d{1})\.?(\d{2})\.?(\d{4})': 
                r'\1-\2.\3.\4.\5.\6',
            
            # CPC article references
            r'art\.?\s*(\d+).*?cpc': r'art. \1 do CPC',
            r'artigo\s*(\d+).*?c[o0]digo.*?pr[o0]cesso': r'artigo \1 do Código de Processo Civil',
            
            # Currency patterns - Brazilian format
            r'R\$?\s*(\d+)\.?(\d{3})\.?(\d{3}),(\d{2})': r'R$ \1.\2.\3,\4',
            r'R\$?\s*(\d+)\.?(\d{3}),(\d{2})': r'R$ \1.\2,\3',
            r'R\$?\s*(\d+),(\d{2})': r'R$ \1,\2',
            
            # Legal reference patterns
            r'lei\s*n[o0º°]?\s*(\d+)': r'Lei nº \1',
            r'decreto\s*n[o0º°]?\s*(\d+)': r'Decreto nº \1',
            
            # Time patterns
            r'(\d{1,2})[h:](\d{2})\s*h?o?r?a?s?': r'\1h\2',
            r'as\s*(\d{1,2})[h:](\d{2})': r'às \1h\2',
            
            # Common legal phrases
            r'nos\s+termos?\s+do?\s+artigo': 'nos termos do artigo',
            r'de\s+acordo\s+com\s+a?\s+lei': 'de acordo com a lei',
            r'pelo\s+presente\s+edital': 'pelo presente edital'
        }
    
    def _build_spacing_patterns(self) -> Dict[str, str]:
        """Build spacing correction patterns"""
        return {
            # Fix missing spaces after punctuation
            r'\.([A-Z])': r'. \1',
            r',([A-Z])': r', \1',
            r';([A-Z])': r'; \1',
            r':([A-Z])': r': \1',
            
            # Fix missing spaces before/after parentheses
            r'([a-z])\(': r'\1 (',
            r'\)([a-z])': r') \1',
            
            # Fix compound words that got split
            r'pro cesso': 'processo',
            r'exe cução': 'execução',
            r'tri bunal': 'tribunal',
            r'có digo': 'código',
            r'ar tigo': 'artigo',
            r'lei lão': 'leilão',
            r'has ta': 'hasta',
            r'pú blica': 'pública',
            
            # Fix extra spaces
            r'\s+': ' ',  # Multiple spaces to single space
            r'^\s+|\s+$': '',  # Trim leading/trailing spaces
        }
    
    def correct_text(self, text: str, confidence_threshold: float = 0.7) -> CorrectionResult:
        """
        Correct OCR text with intelligent error detection and correction
        
        Args:
            text: Raw OCR text to correct
            confidence_threshold: Minimum confidence for corrections
            
        Returns:
            CorrectionResult with corrected text and metadata
        """
        start_time = datetime.now()
        original_text = text
        corrections_made = []
        
        try:
            # Step 1: Character-level corrections
            text, char_corrections = self._apply_character_corrections(text)
            corrections_made.extend(char_corrections)
            
            # Step 2: Word-level corrections
            text, word_corrections = self._apply_word_corrections(text)
            corrections_made.extend(word_corrections)
            
            # Step 3: Pattern-based corrections
            text, pattern_corrections = self._apply_pattern_corrections(text)
            corrections_made.extend(pattern_corrections)
            
            # Step 4: Spacing corrections
            text, spacing_corrections = self._apply_spacing_corrections(text)
            corrections_made.extend(spacing_corrections)
            
            # Step 5: Final validation and cleanup
            text = self._final_cleanup(text)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                original_text, text, corrections_made
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"OCR correction completed: {len(corrections_made)} corrections, "
                       f"confidence: {confidence_score:.2f}")
            
            return CorrectionResult(
                original_text=original_text,
                corrected_text=text,
                corrections_made=corrections_made,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in OCR correction: {e}")
            # Return original text if correction fails
            return CorrectionResult(
                original_text=original_text,
                corrected_text=original_text,
                corrections_made=[],
                confidence_score=0.0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _apply_character_corrections(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply character-level corrections"""
        corrections = []
        corrected_text = text
        
        for error, correction in self.character_corrections.items():
            if error in corrected_text:
                # Context-aware correction for numbers vs letters
                if error in ['0', '1', '8', '6', '5']:
                    # Only correct if in word context, not in numbers
                    pattern = rf'(?<![0-9]){re.escape(error)}(?![0-9])'
                    if re.search(pattern, corrected_text):
                        new_text = re.sub(pattern, correction, corrected_text)
                        if new_text != corrected_text:
                            corrections.append({
                                'type': 'character',
                                'from': error,
                                'to': correction,
                                'context': 'word_context'
                            })
                            corrected_text = new_text
                else:
                    new_text = corrected_text.replace(error, correction)
                    if new_text != corrected_text:
                        corrections.append({
                            'type': 'character',
                            'from': error,
                            'to': correction,
                            'context': 'direct_replacement'
                        })
                        corrected_text = new_text
        
        return corrected_text, corrections
    
    def _apply_word_corrections(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply word-level corrections"""
        corrections = []
        corrected_text = text
        
        for error_word, correct_word in self.word_corrections.items():
            # Word boundary matching to avoid partial replacements
            pattern = rf'\b{re.escape(error_word)}\b'
            matches = re.finditer(pattern, corrected_text, re.IGNORECASE)
            
            for match in matches:
                corrections.append({
                    'type': 'word',
                    'from': match.group(),
                    'to': correct_word,
                    'position': match.start()
                })
            
            corrected_text = re.sub(pattern, correct_word, corrected_text, flags=re.IGNORECASE)
        
        return corrected_text, corrections
    
    def _apply_pattern_corrections(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply pattern-based corrections"""
        corrections = []
        corrected_text = text
        
        for pattern, replacement in self.legal_patterns.items():
            matches = re.finditer(pattern, corrected_text, re.IGNORECASE)
            
            for match in matches:
                old_text = match.group()
                new_text = re.sub(pattern, replacement, old_text, flags=re.IGNORECASE)
                
                if new_text != old_text:
                    corrections.append({
                        'type': 'pattern',
                        'from': old_text,
                        'to': new_text,
                        'pattern': pattern
                    })
            
            corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
        
        return corrected_text, corrections
    
    def _apply_spacing_corrections(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply spacing corrections"""
        corrections = []
        corrected_text = text
        
        for pattern, replacement in self.spacing_patterns.items():
            old_text = corrected_text
            corrected_text = re.sub(pattern, replacement, corrected_text)
            
            if corrected_text != old_text:
                corrections.append({
                    'type': 'spacing',
                    'description': f'Applied pattern: {pattern}',
                    'changes_count': len(re.findall(pattern, old_text))
                })
        
        return corrected_text, corrections
    
    def _final_cleanup(self, text: str) -> str:
        """Final text cleanup and normalization"""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Normalize dashes
        text = text.replace('–', '-').replace('—', '-')
        
        # Ensure proper capitalization after periods
        text = re.sub(r'\.(\s+)([a-z])', lambda m: '.' + m.group(1) + m.group(2).upper(), text)
        
        return text
    
    def _calculate_confidence_score(self, original: str, corrected: str, corrections: List[Dict]) -> float:
        """Calculate confidence score for the correction process"""
        
        if not original:
            return 0.0
        
        if original == corrected:
            return 1.0  # No corrections needed = high confidence
        
        # Base confidence on number and type of corrections
        base_confidence = 0.8
        
        # Reduce confidence based on correction density
        correction_density = len(corrections) / len(original.split())
        confidence_penalty = min(0.3, correction_density * 0.1)
        
        # Adjust based on correction types
        type_weights = {
            'character': 0.95,  # High confidence in character corrections
            'word': 0.90,       # High confidence in word corrections
            'pattern': 0.85,    # Good confidence in pattern corrections
            'spacing': 0.98     # Very high confidence in spacing corrections
        }
        
        if corrections:
            type_confidence = sum(
                type_weights.get(corr.get('type', 'unknown'), 0.5) 
                for corr in corrections
            ) / len(corrections)
        else:
            type_confidence = 1.0
        
        final_confidence = base_confidence * type_confidence - confidence_penalty
        return max(0.0, min(1.0, final_confidence))
    
    def get_correction_statistics(self, corrections: List[Dict]) -> Dict[str, Any]:
        """Get statistics about corrections made"""
        
        stats = {
            'total_corrections': len(corrections),
            'correction_types': {},
            'most_common_corrections': {},
            'confidence_metrics': {}
        }
        
        # Count by type
        for correction in corrections:
            corr_type = correction.get('type', 'unknown')
            stats['correction_types'][corr_type] = stats['correction_types'].get(corr_type, 0) + 1
        
        # Most common specific corrections
        for correction in corrections:
            if 'from' in correction and 'to' in correction:
                key = f"{correction['from']} → {correction['to']}"
                stats['most_common_corrections'][key] = stats['most_common_corrections'].get(key, 0) + 1
        
        # Sort most common corrections
        stats['most_common_corrections'] = dict(
            sorted(stats['most_common_corrections'].items(), 
                   key=lambda x: x[1], reverse=True)[:10]
        )
        
        return stats

# Global corrector instance
ocr_text_corrector = OCRTextCorrector()

def correct_ocr_text(text: str, confidence_threshold: float = 0.7) -> CorrectionResult:
    """
    Convenience function for OCR text correction
    
    Args:
        text: Raw OCR text to correct
        confidence_threshold: Minimum confidence for corrections
        
    Returns:
        CorrectionResult with corrected text and metadata
    """
    return ocr_text_corrector.correct_text(text, confidence_threshold)