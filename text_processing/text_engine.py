"""
Text Processing Engine - Etapa 3
Processamento de texto, detecção de idioma, extração de entidades e identificação de leads
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from dataclasses import dataclass, asdict

# NLP Libraries
try:
    import spacy
    from spacy import displacy
    import langdetect
    from langdetect import detect, detect_langs
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy não está disponível - usando processamento básico")

# Text processing libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, SnowballStemmer
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
    
    # Download required NLTK data if not present
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
        
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger')
        
    try:
        nltk.data.find('chunkers/maxent_ne_chunker')
    except LookupError:
        nltk.download('maxent_ne_chunker')
        
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words')
        
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK não está disponível - usando processamento básico")

logger = logging.getLogger(__name__)

@dataclass
class EntityMatch:
    """Entidade extraída do texto"""
    text: str
    entity_type: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str
    metadata: Dict[str, Any] = None

@dataclass
class TextProcessingResult:
    """Resultado do processamento de texto"""
    job_id: str
    page_number: int
    original_text: str
    cleaned_text: str
    detected_language: str
    language_confidence: float
    entities: List[EntityMatch]
    keywords: List[str]
    sentences: List[str]
    word_count: int
    char_count: int
    lead_indicators: Dict[str, Any]
    processing_metadata: Dict[str, Any]
    processed_at: str

class TextEngine:
    """Engine principal de processamento de texto"""
    
    # Padrões regex para extração de entidades brasileiras
    PATTERNS = {
        'cnpj': r'\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}',
        'cpf': r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
        'phone': r'(?:\+55\s?)?(?:\(\d{2}\)\s?)?(?:9\s?)?\d{4}[-\s]?\d{4}',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'cep': r'\d{5}-?\d{3}',
        'money': r'R\$\s?[\d.,]+(?:\.\d{2})?',
        'percentage': r'\d+(?:,\d+)?%',
        'website': r'https?://[^\s]+|www\.[^\s]+',
        'company_suffix': r'\b(?:LTDA|ME|EPP|EIRELI|S\.A\.|SA|LDTA)\b',
    }
    
    # Palavras-chave para detecção de oportunidades
    LEAD_KEYWORDS = {
        'opportunity': [
            'oportunidade', 'negócio', 'projeto', 'contrato', 'licitação',
            'edital', 'concorrência', 'proposta', 'orçamento', 'investimento'
        ],
        'decision_makers': [
            'diretor', 'gerente', 'coordenador', 'supervisor', 'responsável',
            'presidente', 'vice-presidente', 'ceo', 'cto', 'cfo'
        ],
        'company_indicators': [
            'empresa', 'corporação', 'organização', 'instituição', 'fundação',
            'faturamento', 'receita', 'lucro', 'funcionários', 'colaboradores'
        ],
        'urgency': [
            'urgente', 'imediato', 'prazo', 'deadline', 'asap', 'breve',
            'rápido', 'emergência', 'prioridade'
        ],
        'technology': [
            'sistema', 'software', 'tecnologia', 'digital', 'automação',
            'integração', 'api', 'banco de dados', 'nuvem', 'cloud'
        ]
    }
    
    def __init__(self):
        """Inicializa o engine de processamento de texto"""
        logger.info("TextEngine inicializado")
    
    def process_text(self, text: str, job_id: str, page_number: int) -> TextProcessingResult:
        """Processa texto completo com todas as etapas"""
        try:
            start_time = datetime.now()
            
            # 1. Limpeza e normalização
            cleaned_text = self.clean_and_normalize_text(text)
            
            # 2. Detecção de idioma
            detected_lang, lang_confidence = self.detect_language(cleaned_text)
            
            # 3. Tokenização e análise básica
            sentences = self.extract_sentences(cleaned_text)
            word_count = len(cleaned_text.split())
            char_count = len(cleaned_text)
            
            # 4. Extração de entidades
            entities = self.extract_entities(cleaned_text, detected_lang)
            
            # 5. Extração de palavras-chave
            keywords = self.extract_keywords(cleaned_text, detected_lang)
            
            # 6. Análise de indicadores de leads
            lead_indicators = self.analyze_lead_potential(cleaned_text, entities, keywords)
            
            # 7. Metadados de processamento
            processing_time = (datetime.now() - start_time).total_seconds()
            processing_metadata = {
                'processing_time': processing_time,
                'entity_extraction_method': 'regex',
                'text_quality_score': self._calculate_text_quality(cleaned_text),
                'language_detection_method': 'heuristic'
            }
            
            result = TextProcessingResult(
                job_id=job_id,
                page_number=page_number,
                original_text=text,
                cleaned_text=cleaned_text,
                detected_language=detected_lang,
                language_confidence=lang_confidence,
                entities=entities,
                keywords=keywords,
                sentences=sentences,
                word_count=word_count,
                char_count=char_count,
                lead_indicators=lead_indicators,
                processing_metadata=processing_metadata,
                processed_at=datetime.now().isoformat()
            )
            
            logger.info(f"Texto processado para job {job_id}, página {page_number}: "
                       f"{word_count} palavras, {len(entities)} entidades, "
                       f"{len(keywords)} palavras-chave")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento de texto: {e}")
            return TextProcessingResult(
                job_id=job_id,
                page_number=page_number,
                original_text=text,
                cleaned_text=text,
                detected_language='unknown',
                language_confidence=0.0,
                entities=[],
                keywords=[],
                sentences=[],
                word_count=len(text.split()),
                char_count=len(text),
                lead_indicators={},
                processing_metadata={'error': str(e)},
                processed_at=datetime.now().isoformat()
            )
    
    def clean_and_normalize_text(self, text: str) -> str:
        """Limpa e normaliza o texto"""
        if not text:
            return ""
        
        # Remover caracteres de controle e espaços extras
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        
        return text
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detecta o idioma do texto"""
        try:
            if len(text.strip()) < 10:
                return 'unknown', 0.0
            
            # Análise básica de palavras comuns
            pt_indicators = ['e', 'de', 'da', 'do', 'em', 'com', 'para', 'por', 'que', 'não']
            en_indicators = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']
            
            words = text.lower().split()
            pt_count = sum(1 for word in words if word in pt_indicators)
            en_count = sum(1 for word in words if word in en_indicators)
            
            if pt_count > en_count:
                return 'pt', min(0.8, pt_count / len(words) * 2)
            elif en_count > 0:
                return 'en', min(0.8, en_count / len(words) * 2)
            else:
                return 'unknown', 0.0
                
        except Exception as e:
            logger.warning(f"Erro na detecção de idioma: {e}")
            return 'unknown', 0.0
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extrai sentenças do texto"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_entities(self, text: str, language: str) -> List[EntityMatch]:
        """Extrai entidades do texto usando padrões regex"""
        entities = []
        
        for entity_type, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(EntityMatch(
                    text=match.group(),
                    entity_type=entity_type,
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    context=text[max(0, match.start()-50):match.end()+50],
                    metadata={'method': 'regex', 'pattern': pattern}
                ))
        
        # Remover duplicatas
        unique_entities = []
        seen = set()
        for entity in entities:
            key = (entity.text.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_keywords(self, text: str, language: str) -> List[str]:
        """Extrai palavras-chave relevantes do texto"""
        try:
            # Tokenizar e filtrar palavras
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Stopwords básicas
            stopwords = ['de', 'da', 'do', 'e', 'em', 'com', 'para', 'por', 'que', 'não', 'o', 'a', 'os', 'as']
            
            # Filtrar palavras curtas, números e stopwords
            filtered_words = []
            for word in words:
                if (len(word) >= 3 and 
                    not word.isdigit() and 
                    word not in stopwords):
                    filtered_words.append(word)
            
            # Contar frequência
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Selecionar as mais frequentes
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, freq in sorted_words[:20] if freq > 1]
            
            return keywords
            
        except Exception as e:
            logger.warning(f"Erro na extração de palavras-chave: {e}")
            return []
    
    def analyze_lead_potential(self, text: str, entities: List[EntityMatch], keywords: List[str]) -> Dict[str, Any]:
        """Analisa o potencial de lead do texto"""
        lead_indicators = {
            'has_contact_info': False,
            'has_company_info': False,
            'has_opportunity_keywords': False,
            'has_financial_info': False,
            'urgency_level': 'low',
            'decision_maker_present': False,
            'technology_related': False,
            'lead_score': 0.0,
            'confidence': 0.0
        }
        
        text_lower = text.lower()
        score = 0.0
        confidence_factors = []
        
        # Verificar informações de contato
        contact_entities = [e for e in entities if e.entity_type in ['email', 'phone', 'cnpj', 'cpf']]
        if contact_entities:
            lead_indicators['has_contact_info'] = True
            score += 25
            confidence_factors.append(f"{len(contact_entities)} contatos encontrados")
        
        # Verificar informações de empresa
        company_entities = [e for e in entities if e.entity_type in ['cnpj', 'company_suffix']]
        if company_entities:
            lead_indicators['has_company_info'] = True
            score += 20
            confidence_factors.append("Informações de empresa presentes")
        
        # Verificar palavras-chave de oportunidade
        opportunity_matches = []
        for category, words in self.LEAD_KEYWORDS.items():
            matches = [word for word in words if word in text_lower]
            if matches:
                opportunity_matches.extend(matches)
                if category == 'opportunity':
                    lead_indicators['has_opportunity_keywords'] = True
                    score += 30
                elif category == 'decision_makers':
                    lead_indicators['decision_maker_present'] = True
                    score += 15
                elif category == 'urgency':
                    lead_indicators['urgency_level'] = 'high'
                    score += 10
                elif category == 'technology':
                    lead_indicators['technology_related'] = True
                    score += 10
        
        # Verificar informações financeiras
        financial_entities = [e for e in entities if e.entity_type in ['money', 'percentage']]
        if financial_entities:
            lead_indicators['has_financial_info'] = True
            score += 20
            confidence_factors.append(f"{len(financial_entities)} valores financeiros")
        
        # Calcular score final
        lead_indicators['lead_score'] = min(100.0, score)
        lead_indicators['confidence'] = min(1.0, len(confidence_factors) / 5.0)
        lead_indicators['matched_keywords'] = opportunity_matches
        lead_indicators['confidence_factors'] = confidence_factors
        
        return lead_indicators
    
    def _calculate_text_quality(self, text: str) -> float:
        """Calcula um score de qualidade do texto"""
        if not text:
            return 0.0
        
        score = 0.0
        
        # Fator 1: Comprimento
        length_score = min(1.0, len(text) / 1000.0) if len(text) < 1000 else max(0.5, 1000.0 / len(text))
        score += length_score * 0.3
        
        # Fator 2: Proporção de caracteres alfabéticos
        alpha_ratio = sum(1 for c in text if c.isalpha()) / len(text)
        score += alpha_ratio * 0.3
        
        # Fator 3: Presença de pontuação
        punct_chars = '.!?,:;'
        punct_ratio = min(0.1, sum(1 for c in text if c in punct_chars) / len(text))
        score += punct_ratio * 0.2
        
        # Fator 4: Diversidade de palavras
        words = text.split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            score += unique_ratio * 0.2
        
        return min(1.0, score)

# Instância global do engine
text_engine = TextEngine() 