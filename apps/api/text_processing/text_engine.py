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
    
    # Padrões regex para extração de entidades brasileiras de leilões judiciais
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
        
        # Padrões específicos para leilões judiciais
        'process_number': r'\d{7}-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',  # Número de processo judicial
        'property_registration': r'(?:matrícula|registro)\s*n?º?\s*\d+',  # Matrícula do imóvel
        'auction_date': r'\d{1,2}\/\d{1,2}\/\d{4}',  # Datas de leilão
        'auction_value': r'(?:lance|avaliação|valor)\s*(?:mínimo|inicial)?\s*:?\s*R\$\s?[\d.,]+',
        'property_area': r'\d+(?:,\d+)?\s*m²',  # Área do imóvel
        'iptu_value': r'IPTU\s*:?\s*R\$\s?[\d.,]+',  # Valor do IPTU
        'debt_value': r'(?:débito|dívida)\s*:?\s*R\$\s?[\d.,]+',  # Valores de débito
        'court_name': r'\d+ª?\s*Vara\s*(?:Cível|Criminal|Execução)?',  # Nome da vara
    }
    
    # Palavras-chave específicas para leilões judiciais brasileiros
    LEAD_KEYWORDS = {
        'judicial_auction': [
            'leilão judicial', 'hasta pública', 'arrematação', 'execução fiscal',
            'penhora', 'alienação judicial', 'hasta', 'leilão', 'arrematante',
            'adjudicação', 'execução', 'expropriação'
        ],
        'legal_notifications': [
            'edital', 'intimação', 'citação', 'diário oficial', 'publicação',
            'notificação', 'cientificação', 'comunicação', 'aviso',
            'art. 889', 'CPC', 'código de processo civil'
        ],
        'property_valuation': [
            'avaliação', 'laudo', 'perícia', 'valor de mercado', 'valor venal',
            'valor da avaliação', 'preço', 'lance mínimo', 'primeira praça',
            'segunda praça', 'valor inicial'
        ],
        'property_status': [
            'imóvel desocupado', 'livre de ocupação', 'desimpedido',
            'sem ocupantes', 'vago', 'livre', 'desembaraçado',
            'inquilino', 'locatário', 'posseiro', 'ocupação irregular'
        ],
        'legal_compliance': [
            'regular', 'conforme', 'legal', 'válido', 'procedimento correto',
            'dentro do prazo', 'publicado', 'intimado', 'notificado',
            'cumprimento', 'observância'
        ],
        'financial_data': [
            'débito', 'dívida', 'IPTU', 'condomínio', 'taxa', 'imposto',
            'financiamento', 'hipoteca', 'ônus', 'gravame', 'encargo',
            'quitação', 'pagamento'
        ],
        'legal_restrictions': [
            'indisponibilidade', 'penhora', 'arresto', 'sequestro',
            'bloqueio', 'restrição', 'impedimento', 'gravame',
            'ônus real', 'usufruto', 'servidão'
        ],
        'investment_opportunity': [
            'oportunidade', 'investimento', 'negócio', 'aquisição',
            'compra', 'desconto', 'abaixo do mercado', 'barganha',
            'rentabilidade', 'valorização'
        ],
        'urgency_indicators': [
            'prazo', 'vencimento', 'data limite', 'até', 'antes de',
            'urgente', 'imediato', 'breve', 'em breve'
        ],
        'decision_authorities': [
            'juiz', 'magistrado', 'leiloeiro', 'oficial de justiça',
            'escrivão', 'cartório', 'tribunal', 'vara', 'foro',
            'comarca', 'instância'
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
        """Analisa o potencial de investimento em leilão judicial"""
        lead_indicators = {
            'has_judicial_auction': False,
            'has_legal_notifications': False,
            'has_property_valuation': False,
            'has_property_status': False,
            'has_legal_compliance': False,
            'has_financial_data': False,
            'legal_restrictions_level': 'unknown',
            'investment_viability': 'low',
            'lead_score': 0.0,
            'confidence': 0.0,
            'risk_level': 'high'
        }
        
        text_lower = text.lower()
        score = 0.0
        confidence_factors = []
        risk_factors = []
        
        # 1. Confirmação de leilão judicial (+30 pontos)
        judicial_matches = []
        for word in self.LEAD_KEYWORDS['judicial_auction']:
            if word in text_lower:
                judicial_matches.append(word)
        
        if judicial_matches:
            lead_indicators['has_judicial_auction'] = True
            score += 30
            confidence_factors.append(f"Leilão judicial confirmado: {len(judicial_matches)} indicadores")
        
        # 2. Publicações e notificações legais (+25 pontos)
        legal_notification_matches = []
        for word in self.LEAD_KEYWORDS['legal_notifications']:
            if word in text_lower:
                legal_notification_matches.append(word)
        
        if legal_notification_matches:
            lead_indicators['has_legal_notifications'] = True
            score += 25
            confidence_factors.append(f"Notificações legais: {len(legal_notification_matches)} encontradas")
        
        # 3. Dados financeiros e avaliações (+20 pontos)
        valuation_matches = []
        for word in self.LEAD_KEYWORDS['property_valuation']:
            if word in text_lower:
                valuation_matches.append(word)
        
        financial_entities = [e for e in entities if e.entity_type in ['money', 'auction_value', 'iptu_value', 'debt_value']]
        if valuation_matches or financial_entities:
            lead_indicators['has_property_valuation'] = True
            score += 20
            confidence_factors.append(f"Dados financeiros: {len(valuation_matches)} + {len(financial_entities)} valores")
        
        # 4. Status de ocupação/posse (+15 pontos)
        property_status_matches = []
        for word in self.LEAD_KEYWORDS['property_status']:
            if word in text_lower:
                property_status_matches.append(word)
        
        if property_status_matches:
            lead_indicators['has_property_status'] = True
            # Verificar se é positivo (desocupado) ou negativo (ocupado)
            positive_status = ['desocupado', 'livre', 'vago', 'desembaraçado', 'sem ocupantes']
            negative_status = ['inquilino', 'locatário', 'posseiro', 'ocupação irregular']
            
            positive_count = sum(1 for word in positive_status if word in text_lower)
            negative_count = sum(1 for word in negative_status if word in text_lower)
            
            if positive_count > negative_count:
                score += 15
                confidence_factors.append("Imóvel livre de ocupação")
            else:
                score += 5
                risk_factors.append("Possível ocupação irregular")
        
        # 5. Conformidade legal (+10 pontos)
        compliance_matches = []
        for word in self.LEAD_KEYWORDS['legal_compliance']:
            if word in text_lower:
                compliance_matches.append(word)
        
        if compliance_matches:
            lead_indicators['has_legal_compliance'] = True
            score += 10
            confidence_factors.append(f"Conformidade legal: {len(compliance_matches)} indicadores")
        
        # 6. Verificar restrições legais (reduz pontuação)
        restriction_matches = []
        for word in self.LEAD_KEYWORDS['legal_restrictions']:
            if word in text_lower:
                restriction_matches.append(word)
        
        if restriction_matches:
            restriction_penalty = min(15, len(restriction_matches) * 3)
            score -= restriction_penalty
            risk_factors.append(f"Restrições legais: {len(restriction_matches)} encontradas")
            lead_indicators['legal_restrictions_level'] = 'high' if len(restriction_matches) > 2 else 'medium'
        else:
            lead_indicators['legal_restrictions_level'] = 'low'
        
        # 7. Oportunidade de investimento (bônus)
        investment_matches = []
        for word in self.LEAD_KEYWORDS['investment_opportunity']:
            if word in text_lower:
                investment_matches.append(word)
        
        if investment_matches:
            score += 5
            confidence_factors.append(f"Oportunidade de investimento: {len(investment_matches)} indicadores")
        
        # 8. Urgência (pode ser positiva ou negativa)
        urgency_matches = []
        for word in self.LEAD_KEYWORDS['urgency_indicators']:
            if word in text_lower:
                urgency_matches.append(word)
        
        if urgency_matches:
            score += 5
            confidence_factors.append(f"Indicadores de prazo: {len(urgency_matches)}")
        
        # 9. Verificar entidades específicas de leilão
        judicial_entities = [e for e in entities if e.entity_type in ['process_number', 'property_registration', 'auction_date', 'court_name']]
        if judicial_entities:
            score += 10
            confidence_factors.append(f"Entidades judiciais: {len(judicial_entities)} encontradas")
        
        # Calcular score final e métricas
        lead_indicators['lead_score'] = max(0.0, min(100.0, score))
        lead_indicators['confidence'] = min(1.0, len(confidence_factors) / 6.0)
        
        # Determinar viabilidade de investimento
        if score >= 70:
            lead_indicators['investment_viability'] = 'high'
            lead_indicators['risk_level'] = 'low'
        elif score >= 50:
            lead_indicators['investment_viability'] = 'medium'
            lead_indicators['risk_level'] = 'medium'
        else:
            lead_indicators['investment_viability'] = 'low'
            lead_indicators['risk_level'] = 'high'
        
        # Adicionar fatores de análise
        all_matches = judicial_matches + legal_notification_matches + valuation_matches + property_status_matches + compliance_matches
        lead_indicators['matched_keywords'] = all_matches
        lead_indicators['confidence_factors'] = confidence_factors
        lead_indicators['risk_factors'] = risk_factors
        
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