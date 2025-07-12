"""
Legal Text Enhancer - Week 2 Implementation
Specialized text enhancement for Brazilian legal documents and judicial auctions
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class LegalEnhancementResult:
    """Result of legal text enhancement"""
    original_text: str
    enhanced_text: str
    legal_corrections: List[Dict[str, str]]
    standardizations: List[Dict[str, str]]
    confidence_score: float
    legal_terms_found: int
    processing_time: float

class LegalTextEnhancer:
    """
    Brazilian legal document text enhancer
    Specialized for judicial auction documents and legal terminology
    """
    
    def __init__(self):
        """Initialize with Brazilian legal domain knowledge"""
        self.legal_terms = self._build_legal_terminology()
        self.court_names = self._build_court_standardization()
        self.legal_phrases = self._build_legal_phrases()
        self.process_patterns = self._build_process_patterns()
        self.legal_abbreviations = self._build_legal_abbreviations()
        
        logger.info("Legal Text Enhancer initialized with Brazilian legal domain")
    
    def _build_legal_terminology(self) -> Dict[str, str]:
        """Build comprehensive legal terminology corrections"""
        return {
            # Auction specific terms
            'leil5o': 'leilão',
            'leilao': 'leilão', 
            'leil50': 'leilão',
            'leiI5o': 'leilão',
            'hasfa': 'hasta',
            'hasta': 'hasta',
            'h5sta': 'hasta',
            'publica': 'pública',
            'pub1ica': 'pública',
            'publìca': 'pública',
            
            # Execution terms
            'execu§5o': 'execução',
            'execucao': 'execução',
            'execu§ao': 'execução',
            'exec11§5o': 'execução',
            'penf1ora': 'penhora',
            'penfiora': 'penhora',
            'pen1iora': 'penhora',
            'arrematacao': 'arrematação',
            'arremata§ao': 'arrematação',
            'adj11dica§5o': 'adjudicação',
            'adjudicacao': 'adjudicação',
            
            # Legal procedures
            'cita§5o': 'citação',
            'citacao': 'citação',
            'cìta§5o': 'citação',
            'intima§5o': 'intimação',
            'intimacao': 'intimação',
            'ìntima§5o': 'intimação',
            'notifica§5o': 'notificação',
            'notificacao': 'notificação',
            'publica§5o': 'publicação',
            'publicacao': 'publicação',
            
            # Property terms
            'ìm6vel': 'imóvel',
            'imovel': 'imóvel',
            'im6vel': 'imóvel',
            'ìmoveI': 'imóvel',
            'propríedade': 'propriedade',
            'propriedade': 'propriedade',
            'edìficio': 'edifício',
            'edificio': 'edifício',
            'edífìcio': 'edifício',
            'apartament0': 'apartamento',
            'apartamento': 'apartamento',
            
            # Legal entities
            'tribun5l': 'tribunal',
            'tribunal': 'tribunal',
            'trìbunal': 'tribunal',
            'jui2o': 'juízo',
            'juizo': 'juízo',
            'juí2o': 'juízo',
            'c0marca': 'comarca',
            'comarca': 'comarca',
            'c6marca': 'comarca',
            'f0ro': 'foro',
            'foro': 'foro',
            'cartorìo': 'cartório',
            'cartorio': 'cartório',
            
            # Legal professionals
            'advog5do': 'advogado',
            'advogado': 'advogado',
            'procur5dor': 'procurador',
            'procurador': 'procurador',
            'escríváo': 'escrivão',
            'escrivao': 'escrivão',
            'leiloeiro': 'leiloeiro',
            'leìloeiro': 'leiloeiro',
            
            # Legal documents
            'matr1cula': 'matrícula',
            'matricula': 'matrícula',
            'certid5o': 'certidão',
            'certidao': 'certidão',
            'mandad0': 'mandado',
            'mandado': 'mandado',
            'edìtal': 'edital',
            'edital': 'edital',
            
            # Financial terms
            'avalìa§5o': 'avaliação',
            'avaliacao': 'avaliação',
            'aval1a§5o': 'avaliação',
            'divìda': 'dívida',
            'divida': 'dívida',
            'debìto': 'débito',
            'debito': 'débito',
            'honorarios': 'honorários',
            'honorarios': 'honorários',
            
            # Temporal terms
            'pra2o': 'prazo',
            'prazo': 'prazo',
            'venciment0': 'vencimento',
            'vencimento': 'vencimento',
            'data-limite': 'data-limite',
            
            # Legal status
            'regular': 'regular',
            'ìrregular': 'irregular',
            'irregular': 'irregular',
            'pendencìa': 'pendência',
            'pendencia': 'pendência',
            'inadìmpl': 'inadimpl'
        }
    
    def _build_court_standardization(self) -> Dict[str, str]:
        """Build court name standardization patterns"""
        return {
            # Tribunal variations
            r'T\.?J\.?\s*S\.?P\.?': 'Tribunal de Justiça de São Paulo',
            r'T\.?J\.?\s*R\.?J\.?': 'Tribunal de Justiça do Rio de Janeiro',
            r'T\.?J\.?\s*M\.?G\.?': 'Tribunal de Justiça de Minas Gerais',
            r'T\.?R\.?F\.?\s*1': 'Tribunal Regional Federal da 1ª Região',
            r'T\.?R\.?F\.?\s*2': 'Tribunal Regional Federal da 2ª Região',
            r'T\.?R\.?F\.?\s*3': 'Tribunal Regional Federal da 3ª Região',
            
            # Vara variations
            r'(\d+)[ªº°]?\s*V\.?\s*C[íi]v[ei]l': r'\1ª Vara Cível',
            r'(\d+)[ªº°]?\s*V\.?\s*F[ai]m[íi]lia': r'\1ª Vara de Família',
            r'(\d+)[ªº°]?\s*V\.?\s*Exec': r'\1ª Vara de Execução',
            r'(\d+)[ªº°]?\s*V\.?\s*F[ai]z': r'\1ª Vara da Fazenda',
            
            # Comarca standardization
            r'C[o0]m[a@]rc[a@]\s+de\s+([A-Z][a-z]+)': r'Comarca de \1',
            r'F[o0]r[o0]\s+de\s+([A-Z][a-z]+)': r'Foro de \1'
        }
    
    def _build_legal_phrases(self) -> Dict[str, str]:
        """Build legal phrase standardization"""
        return {
            # Common legal expressions
            r'nos\s+termos?\s+do?\s+art\.?\s*(\d+)': r'nos termos do art. \1',
            r'de\s+acordo\s+com\s+o?\s+disposto': 'de acordo com o disposto',
            r'pelo\s+presente\s+edital': 'pelo presente edital',
            r'torna\s+p[úu]blico\s+que': 'torna público que',
            r'far[aá]\s+saber\s+aos': 'fará saber aos',
            r'cumpre\s+determina[çc][ãa]o': 'cumpre determinação',
            
            # CPC references
            r'C[óo]digo\s+de?\s+Processo\s+C[íi]vil': 'Código de Processo Civil',
            r'C\.?P\.?C\.?': 'CPC',
            r'art\.?\s*(\d+)\s*do?\s*C\.?P\.?C\.?': r'art. \1 do CPC',
            
            # Legal procedure phrases
            r'realizada?\s+hasta\s+p[úu]blica': 'realizada hasta pública',
            r'ser[áa]\s+realizada?\s+leil[ãa]o': 'será realizado leilão',
            r'melhor\s+lance\s+oferecido': 'melhor lance oferecido',
            r'lance\s+m[íi]nimo': 'lance mínimo',
            r'valor\s+da?\s+avalia[çc][ãa]o': 'valor da avaliação',
            
            # Property descriptions
            r'im[óo]vel\s+situado': 'imóvel situado',
            r'localizado\s+na?\s+rua': 'localizado na Rua',
            r'matr[íi]cula\s+n[ºo°]?\s*(\d+)': r'matrícula nº \1',
            r'registro\s+de?\s+im[óo]veis': 'Registro de Imóveis',
            
            # Temporal expressions
            r'data\s+do?\s+leil[ãa]o': 'data do leilão',
            r'hor[áa]rio\s*:?\s*(\d{1,2})[h:](\d{2})': r'horário: \1h\2',
            r'pra[zs]o\s+de?\s+(\d+)\s*dias?': r'prazo de \1 dias',
        }
    
    def _build_process_patterns(self) -> Dict[str, str]:
        """Build process number standardization patterns"""
        return {
            # Brazilian process number format: 1234567-89.2023.8.26.0100
            r'(\d{7})-?(\d{2})\.?(\d{4})\.?(\d{1})\.?(\d{2})\.?(\d{4})': 
                r'\1-\2.\3.\4.\5.\6',
            
            # Old format process numbers
            r'(\d{3})\.?(\d{2})\.?(\d{4})\.?(\d{6})-?(\d{1})': 
                r'\1.\2.\3.\4-\5',
            
            # Protocol numbers
            r'protocolo\s*n[ºo°]?\s*(\d+)': r'Protocolo nº \1',
            
            # Distribution numbers
            r'distribui[çc][ãa]o\s*n[ºo°]?\s*(\d+)': r'Distribuição nº \1'
        }
    
    def _build_legal_abbreviations(self) -> Dict[str, str]:
        """Build legal abbreviation expansions"""
        return {
            'art.': 'artigo',
            'inc.': 'inciso', 
            'par.': 'parágrafo',
            '§': 'parágrafo',
            'fl.': 'folha',
            'fls.': 'folhas',
            'v.': 'verso',
            'p.': 'página',
            'pp.': 'páginas',
            'cf.': 'conforme',
            'rel.': 'relator',
            'rev.': 'revisor',
            'min.': 'ministro',
            'des.': 'desembargador',
            'proc.': 'processo',
            'aut.': 'autos',
            'req.': 'requerente',
            'reqdo.': 'requerido',
            'exec.': 'exequente',
            'execdo.': 'executado'
        }
    
    def enhance_legal_text(self, text: str) -> LegalEnhancementResult:
        """
        Enhance legal text with Brazilian legal domain knowledge
        
        Args:
            text: Raw text to enhance
            
        Returns:
            LegalEnhancementResult with enhanced text and metadata
        """
        start_time = datetime.now()
        original_text = text
        legal_corrections = []
        standardizations = []
        
        try:
            # Step 1: Legal terminology corrections
            text, term_corrections = self._apply_legal_terminology(text)
            legal_corrections.extend(term_corrections)
            
            # Step 2: Court name standardization
            text, court_corrections = self._apply_court_standardization(text)
            standardizations.extend(court_corrections)
            
            # Step 3: Legal phrase standardization
            text, phrase_corrections = self._apply_legal_phrases(text)
            standardizations.extend(phrase_corrections)
            
            # Step 4: Process number standardization
            text, process_corrections = self._apply_process_patterns(text)
            standardizations.extend(process_corrections)
            
            # Step 5: Abbreviation expansion (optional)
            text, abbrev_corrections = self._expand_abbreviations(text)
            legal_corrections.extend(abbrev_corrections)
            
            # Step 6: Final legal validation
            text = self._final_legal_validation(text)
            
            # Calculate results
            legal_terms_found = self._count_legal_terms(text)
            confidence_score = self._calculate_legal_confidence(
                original_text, text, legal_corrections, standardizations
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Legal enhancement completed: {len(legal_corrections)} corrections, "
                       f"{len(standardizations)} standardizations, "
                       f"{legal_terms_found} legal terms found")
            
            return LegalEnhancementResult(
                original_text=original_text,
                enhanced_text=text,
                legal_corrections=legal_corrections,
                standardizations=standardizations,
                confidence_score=confidence_score,
                legal_terms_found=legal_terms_found,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in legal text enhancement: {e}")
            return LegalEnhancementResult(
                original_text=original_text,
                enhanced_text=original_text,
                legal_corrections=[],
                standardizations=[],
                confidence_score=0.0,
                legal_terms_found=0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _apply_legal_terminology(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply legal terminology corrections"""
        corrections = []
        enhanced_text = text
        
        for error_term, correct_term in self.legal_terms.items():
            pattern = rf'\b{re.escape(error_term)}\b'
            matches = re.finditer(pattern, enhanced_text, re.IGNORECASE)
            
            for match in matches:
                corrections.append({
                    'type': 'legal_terminology',
                    'from': match.group(),
                    'to': correct_term,
                    'position': match.start(),
                    'category': self._get_term_category(correct_term)
                })
            
            enhanced_text = re.sub(pattern, correct_term, enhanced_text, flags=re.IGNORECASE)
        
        return enhanced_text, corrections
    
    def _apply_court_standardization(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply court name standardization"""
        standardizations = []
        enhanced_text = text
        
        for pattern, replacement in self.court_names.items():
            matches = re.finditer(pattern, enhanced_text, re.IGNORECASE)
            
            for match in matches:
                old_text = match.group()
                new_text = re.sub(pattern, replacement, old_text, flags=re.IGNORECASE)
                
                if new_text != old_text:
                    standardizations.append({
                        'type': 'court_standardization',
                        'from': old_text,
                        'to': new_text,
                        'category': 'judicial_entity'
                    })
            
            enhanced_text = re.sub(pattern, replacement, enhanced_text, flags=re.IGNORECASE)
        
        return enhanced_text, standardizations
    
    def _apply_legal_phrases(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply legal phrase standardization"""
        standardizations = []
        enhanced_text = text
        
        for pattern, replacement in self.legal_phrases.items():
            matches = re.finditer(pattern, enhanced_text, re.IGNORECASE)
            
            for match in matches:
                old_text = match.group()
                new_text = re.sub(pattern, replacement, old_text, flags=re.IGNORECASE)
                
                if new_text != old_text:
                    standardizations.append({
                        'type': 'legal_phrase',
                        'from': old_text,
                        'to': new_text,
                        'category': 'legal_expression'
                    })
            
            enhanced_text = re.sub(pattern, replacement, enhanced_text, flags=re.IGNORECASE)
        
        return enhanced_text, standardizations
    
    def _apply_process_patterns(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Apply process number standardization"""
        standardizations = []
        enhanced_text = text
        
        for pattern, replacement in self.process_patterns.items():
            matches = re.finditer(pattern, enhanced_text)
            
            for match in matches:
                old_text = match.group()
                new_text = re.sub(pattern, replacement, old_text)
                
                if new_text != old_text:
                    standardizations.append({
                        'type': 'process_number',
                        'from': old_text,
                        'to': new_text,
                        'category': 'legal_reference'
                    })
            
            enhanced_text = re.sub(pattern, replacement, enhanced_text)
        
        return enhanced_text, standardizations
    
    def _expand_abbreviations(self, text: str, expand: bool = False) -> Tuple[str, List[Dict[str, str]]]:
        """Expand legal abbreviations (optional)"""
        corrections = []
        enhanced_text = text
        
        if not expand:
            return enhanced_text, corrections
        
        for abbrev, expansion in self.legal_abbreviations.items():
            pattern = rf'\b{re.escape(abbrev)}\b'
            matches = re.finditer(pattern, enhanced_text, re.IGNORECASE)
            
            for match in matches:
                corrections.append({
                    'type': 'abbreviation_expansion',
                    'from': match.group(),
                    'to': expansion,
                    'category': 'legal_abbreviation'
                })
            
            enhanced_text = re.sub(pattern, expansion, enhanced_text, flags=re.IGNORECASE)
        
        return enhanced_text, corrections
    
    def _final_legal_validation(self, text: str) -> str:
        """Final validation and cleanup for legal text"""
        
        # Ensure proper capitalization for legal entities
        legal_entities = [
            'Tribunal', 'Vara', 'Juízo', 'Comarca', 'Foro', 'Cartório',
            'Ministério Público', 'Defensoria Pública', 'Ordem dos Advogados'
        ]
        
        for entity in legal_entities:
            # Capitalize first occurrence in sentences
            pattern = rf'(?<=\. ){entity.lower()}'
            text = re.sub(pattern, entity, text, flags=re.IGNORECASE)
        
        # Ensure proper formatting for currency
        text = re.sub(r'R\$\s*(\d)', r'R$ \1', text)
        
        # Ensure proper spacing in legal references
        text = re.sub(r'art\.(\d)', r'art. \1', text)
        text = re.sub(r'§(\d)', r'§ \1', text)
        
        return text
    
    def _get_term_category(self, term: str) -> str:
        """Get category for legal term"""
        categories = {
            'auction': ['leilão', 'hasta', 'arrematação', 'adjudicação'],
            'procedure': ['execução', 'citação', 'intimação', 'notificação'],
            'property': ['imóvel', 'propriedade', 'edifício', 'apartamento'],
            'court': ['tribunal', 'vara', 'juízo', 'comarca', 'foro'],
            'professional': ['advogado', 'procurador', 'escrivão', 'leiloeiro'],
            'document': ['matrícula', 'certidão', 'mandado', 'edital'],
            'financial': ['avaliação', 'dívida', 'débito', 'honorários']
        }
        
        for category, terms in categories.items():
            if any(t in term.lower() for t in terms):
                return category
        
        return 'general'
    
    def _count_legal_terms(self, text: str) -> int:
        """Count legal terms found in text"""
        legal_terms = set(self.legal_terms.values())
        text_lower = text.lower()
        
        count = 0
        for term in legal_terms:
            count += text_lower.count(term.lower())
        
        return count
    
    def _calculate_legal_confidence(self, original: str, enhanced: str, 
                                  corrections: List[Dict], standardizations: List[Dict]) -> float:
        """Calculate confidence score for legal enhancement"""
        
        if not original:
            return 0.0
        
        # Base confidence
        base_confidence = 0.85
        
        # Factor in number of legal terms found
        legal_terms_count = self._count_legal_terms(enhanced)
        text_length = len(enhanced.split())
        
        if text_length > 0:
            legal_density = legal_terms_count / text_length
            legal_bonus = min(0.1, legal_density * 0.5)
        else:
            legal_bonus = 0.0
        
        # Factor in correction quality
        total_changes = len(corrections) + len(standardizations)
        if total_changes > 0:
            change_density = total_changes / len(original.split())
            if change_density > 0.3:  # Too many changes might indicate poor quality
                confidence_penalty = 0.1
            else:
                confidence_penalty = 0.0
        else:
            confidence_penalty = 0.0
        
        final_confidence = base_confidence + legal_bonus - confidence_penalty
        return max(0.0, min(1.0, final_confidence))

# Global enhancer instance
legal_text_enhancer = LegalTextEnhancer()

def enhance_legal_text(text: str) -> LegalEnhancementResult:
    """
    Convenience function for legal text enhancement
    
    Args:
        text: Raw text to enhance
        
    Returns:
        LegalEnhancementResult with enhanced text and metadata
    """
    return legal_text_enhancer.enhance_legal_text(text)