"""
Enhanced Feature Engineering - Zero Cost Intelligence Improvements
Extends existing feature_engineering.py with advanced ML features for better predictions
"""

import logging
import numpy as np
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import json

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    import spacy
    ADVANCED_LIBS_AVAILABLE = True
except ImportError:
    ADVANCED_LIBS_AVAILABLE = False
    logging.warning("Advanced libraries not available - using fallback implementations")

logger = logging.getLogger(__name__)

@dataclass
class EnhancedFeatureSet:
    """Extended feature set with advanced intelligence features"""
    
    # Basic identification (from original)
    job_id: str
    page_number: int = 0
    
    # ENHANCED TEXT STATISTICS (Week 1 improvements)
    text_length: int = 0
    word_count: int = 0
    sentence_count: int = 0
    avg_word_length: float = 0.0
    avg_sentence_length: float = 0.0
    capital_letter_ratio: float = 0.0
    digit_ratio: float = 0.0
    punctuation_density: float = 0.0
    
    # ADVANCED LEGAL PATTERNS (Brazilian specific)
    processo_numbers: int = 0  # Legal process numbers
    cpc_references: int = 0    # CPC (Civil Process Code) references
    lei_references: int = 0    # Law references
    court_references: int = 0  # Court/tribunal mentions
    deadline_mentions: int = 0 # Deadline/prazo mentions
    legal_persons: int = 0     # Legal professionals
    
    # ENHANCED FINANCIAL FEATURES
    currency_mentions: int = 0
    max_amount: float = 0.0
    min_amount: float = 0.0
    avg_amount: float = 0.0
    amount_variance: float = 0.0
    tax_mentions: int = 0      # IPTU, ITBI, etc.
    debt_indicators: int = 0   # Debt-related terms
    payment_terms: int = 0     # Payment methods
    
    # LEGAL ENTITY RECOGNITION (Enhanced)
    property_types: int = 0         # Types of property mentioned
    legal_procedures: int = 0       # Legal procedure terms
    risk_indicators: int = 0        # Risk-related terms
    opportunity_indicators: int = 0 # Investment opportunity terms
    compliance_indicators: int = 0  # Legal compliance terms
    
    # DOCUMENT STRUCTURE ANALYSIS
    has_header: bool = False
    has_footer: bool = False
    has_tables: bool = False
    paragraph_structure_score: float = 0.0
    section_organization_score: float = 0.0
    
    # TF-IDF FEATURES (Legal domain specific)
    legal_tfidf_score: float = 0.0
    financial_tfidf_score: float = 0.0
    procedural_tfidf_score: float = 0.0
    
    # N-GRAM FEATURES (Legal phrases)
    legal_bigrams: int = 0
    legal_trigrams: int = 0
    judicial_phrases: int = 0
    
    # RISK ASSESSMENT FEATURES
    high_risk_patterns: int = 0
    medium_risk_patterns: int = 0
    low_risk_patterns: int = 0
    risk_mitigation_mentions: int = 0
    
    # DOCUMENT QUALITY INDICATORS
    completeness_score: float = 0.0
    clarity_score: float = 0.0
    information_density: float = 0.0
    
    # TEMPORAL FEATURES
    urgency_score: float = 0.0
    deadline_proximity: float = 0.0  # Days until deadline
    temporal_references: int = 0
    
    # DERIVED INTELLIGENCE FEATURES
    investment_attractiveness: float = 0.0
    legal_complexity_score: float = 0.0
    processing_difficulty: float = 0.0
    
    # Metadata
    extraction_confidence: float = 0.0
    processing_time: float = 0.0
    created_at: str = ""

class EnhancedFeatureExtractor:
    """Advanced feature extractor with zero-cost intelligence improvements"""
    
    def __init__(self):
        """Initialize with Brazilian legal domain knowledge"""
        self.legal_vocabulary = self._build_legal_vocabulary()
        self.financial_patterns = self._build_financial_patterns()
        self.risk_patterns = self._build_risk_patterns()
        self.legal_ngrams = self._build_legal_ngrams()
        
        # Initialize TF-IDF vectorizer with legal vocabulary
        if ADVANCED_LIBS_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                vocabulary=list(self.legal_vocabulary.keys()),
                ngram_range=(1, 3),
                max_features=1000,
                stop_words=self._get_legal_stopwords()
            )
            
            # Load Portuguese spaCy model if available
            try:
                self.nlp = spacy.load("pt_core_news_sm")
                logger.info("Portuguese spaCy model loaded successfully")
            except OSError:
                logger.warning("Portuguese spaCy model not found - using regex patterns")
                self.nlp = None
        else:
            self.tfidf_vectorizer = None
            self.nlp = None
        
        logger.info("Enhanced Feature Extractor initialized with Brazilian legal domain knowledge")
    
    def _build_legal_vocabulary(self) -> Dict[str, int]:
        """Build comprehensive legal vocabulary for Brazilian judicial auctions"""
        vocabulary = {}
        index = 0
        
        # Core legal terms
        legal_terms = [
            # Property types
            'imovel', 'propriedade', 'terreno', 'apartamento', 'casa', 'edificio', 
            'comercial', 'residencial', 'rural', 'urbano', 'lote', 'sala',
            
            # Legal procedures  
            'leilao', 'hasta_publica', 'arrematacao', 'execucao', 'penhora', 
            'bloqueio', 'adjudicacao', 'remicao', 'expropriacao', 'alienacao',
            
            # Legal entities
            'tribunal', 'vara', 'juizo', 'comarca', 'juiz', 'escrivao', 
            'oficial', 'leiloeiro', 'advogado', 'procurador', 'curador',
            
            # Financial terms
            'avaliacao', 'lance_minimo', 'debito', 'divida', 'honorarios', 
            'custas', 'iptu', 'itbi', 'condominio', 'financiamento',
            
            # Risk indicators
            'restricao', 'onus', 'gravame', 'hipoteca', 'usufruto', 'servidao', 
            'enfiteuse', 'indisponibilidade', 'arresto', 'sequestro',
            
            # Document types
            'matricula', 'certidao', 'edital', 'auto', 'laudo', 'parecer', 
            'mandado', 'intimacao', 'citacao', 'notificacao',
            
            # Legal references
            'cpc', 'codigo_processo_civil', 'artigo', 'paragrafo', 'inciso', 
            'lei', 'decreto', 'portaria', 'resolucao',
            
            # Temporal terms
            'prazo', 'vencimento', 'data_limite', 'urgente', 'imediato', 
            'breve', 'periodo', 'cronograma',
            
            # Quality indicators
            'regular', 'conforme', 'legal', 'valido', 'procedimento_correto', 
            'publicado', 'intimado', 'notificado'
        ]
        
        for term in legal_terms:
            vocabulary[term] = index
            index += 1
            
        return vocabulary
    
    def _build_financial_patterns(self) -> List[str]:
        """Build financial pattern recognition patterns"""
        return [
            # Brazilian currency patterns
            r'R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?',  # R$ 1.000,00
            r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*reais',  # 1.000,00 reais
            r'valor.*?R\$\s*\d+',  # valor R$ amount
            r'lance.*?R\$\s*\d+',  # lance R$ amount
            r'avaliacao.*?R\$\s*\d+',  # avaliacao R$ amount
            r'debito.*?R\$\s*\d+',  # debito R$ amount
            
            # Tax patterns
            r'iptu.*?R\$\s*\d+',
            r'itbi.*?R\$\s*\d+', 
            r'condominio.*?R\$\s*\d+',
            
            # Percentage patterns
            r'\d+(?:,\d+)?\s*%',  # 10,5%
            r'\d+\s*por\s*cento',  # 10 por cento
        ]
    
    def _build_risk_patterns(self) -> Dict[str, List[str]]:
        """Build risk assessment patterns"""
        return {
            'high_risk': [
                'ocupacao_irregular', 'posseiro', 'invasao', 'litigio', 
                'embargo', 'interdito', 'area_contaminada', 'risco_ambiental',
                'construcao_irregular', 'sem_habite_se', 'acao_demolitoria'
            ],
            'medium_risk': [
                'inquilino', 'locatario', 'condominio_irregular', 'iptu_atrasado',
                'obra_inacabada', 'documentacao_pendente', 'vicio_oculto'
            ],
            'low_risk': [
                'livre_ocupacao', 'desocupado', 'vago', 'documentacao_regular',
                'iptu_em_dia', 'sem_pendencias', 'habite_se_regular'
            ],
            'mitigation': [
                'seguro', 'garantia', 'caucao', 'fianca', 'avalista',
                'consultoria_juridica', 'due_diligence'
            ]
        }
    
    def _build_legal_ngrams(self) -> Dict[str, List[str]]:
        """Build legal n-gram patterns for phrase detection"""
        return {
            'bigrams': [
                'leilao judicial', 'hasta publica', 'execucao fiscal', 
                'lance minimo', 'valor avaliacao', 'divida ativa',
                'codigo processo', 'artigo cpc', 'prazo legal'
            ],
            'trigrams': [
                'codigo processo civil', 'primeira segunda praca',
                'valor lance minimo', 'execucao fiscal fazendaria',
                'hasta publica judicial', 'livre ocupacao imovel'
            ],
            'judicial_phrases': [
                'nos termos do artigo', 'conforme estabelece o cpc',
                'de acordo com a lei', 'cumprindo determinacao judicial',
                'em observancia ao disposto', 'pelo presente edital'
            ]
        }
    
    def _get_legal_stopwords(self) -> List[str]:
        """Get legal domain stopwords to filter out"""
        return [
            'processo', 'autos', 'requerente', 'requerido', 'exequente',
            'executado', 'autor', 'reu', 'parte', 'partes', 'senhor',
            'senhora', 'doutor', 'doutora'
        ]
    
    def extract_enhanced_features(self, text: str, job_id: str = "", page_number: int = 0) -> EnhancedFeatureSet:
        """
        Extract comprehensive enhanced features from text
        
        Args:
            text: Document text to analyze
            job_id: Job identifier
            page_number: Page number
            
        Returns:
            EnhancedFeatureSet with all advanced features
        """
        start_time = datetime.now()
        
        try:
            features = EnhancedFeatureSet(
                job_id=job_id,
                page_number=page_number,
                created_at=datetime.now().isoformat()
            )
            
            # 1. Enhanced text statistics
            features = self._extract_text_statistics(features, text)
            
            # 2. Advanced legal patterns
            features = self._extract_legal_patterns(features, text)
            
            # 3. Enhanced financial features
            features = self._extract_financial_features(features, text)
            
            # 4. Document structure analysis
            features = self._extract_structure_features(features, text)
            
            # 5. TF-IDF features (if available)
            if self.tfidf_vectorizer and ADVANCED_LIBS_AVAILABLE:
                features = self._extract_tfidf_features(features, text)
            
            # 6. N-gram features
            features = self._extract_ngram_features(features, text)
            
            # 7. Risk assessment features
            features = self._extract_risk_features(features, text)
            
            # 8. Quality assessment
            features = self._assess_document_quality(features, text)
            
            # 9. Derived intelligence features
            features = self._calculate_derived_features(features)
            
            # Calculate processing time
            features.processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.debug(f"Enhanced features extracted for {job_id}: "
                        f"completeness={features.completeness_score:.1f}, "
                        f"investment_attractiveness={features.investment_attractiveness:.1f}")
            
            return features
            
        except Exception as e:
            logger.error(f"Error in enhanced feature extraction: {e}")
            # Return basic features in case of error
            return EnhancedFeatureSet(
                job_id=job_id,
                page_number=page_number,
                created_at=datetime.now().isoformat(),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _extract_text_statistics(self, features: EnhancedFeatureSet, text: str) -> EnhancedFeatureSet:
        """Extract advanced text statistics"""
        if not text:
            return features
            
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]
        
        # Basic counts
        features.text_length = len(text)
        features.word_count = len(words)
        features.sentence_count = len(sentences)
        
        # Advanced statistics
        if words:
            features.avg_word_length = sum(len(word) for word in words) / len(words)
        
        if sentences:
            features.avg_sentence_length = sum(len(sent.split()) for sent in sentences) / len(sentences)
        
        # Character composition analysis
        if text:
            features.capital_letter_ratio = sum(1 for c in text if c.isupper()) / len(text)
            features.digit_ratio = sum(1 for c in text if c.isdigit()) / len(text)
            features.punctuation_density = sum(1 for c in text if c in '.,;:!?()[]{}') / len(text)
        
        return features
    
    def _extract_legal_patterns(self, features: EnhancedFeatureSet, text: str) -> EnhancedFeatureSet:
        """Extract legal patterns using Brazilian legal domain knowledge"""
        text_lower = text.lower()
        
        # Legal process numbers (Brazilian format)
        processo_pattern = r'\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}'
        features.processo_numbers = len(re.findall(processo_pattern, text))
        
        # CPC references
        cpc_patterns = [
            r'art\.?\s*\d+.*?cpc',
            r'cpc.*?art\.?\s*\d+',
            r'artigo\s+\d+.*?codigo.*?processo',
            r'codigo.*?processo.*?artigo\s+\d+'
        ]
        features.cpc_references = sum(len(re.findall(pattern, text_lower)) for pattern in cpc_patterns)
        
        # Law references
        lei_patterns = [
            r'lei\s+n[°º]?\s*\d+',
            r'lei\s+federal\s+\d+',
            r'decreto\s+n[°º]?\s*\d+'
        ]
        features.lei_references = sum(len(re.findall(pattern, text_lower)) for pattern in lei_patterns)
        
        # Court references
        court_terms = ['tribunal', 'vara', 'juízo', 'comarca', 'foro', 'instancia']
        features.court_references = sum(text_lower.count(term) for term in court_terms)
        
        # Deadline mentions
        deadline_patterns = [
            r'prazo.*?\d+.*?dias?',
            r'até.*?\d+.*?dias?',
            r'vencimento.*?\d+',
            r'data.*?limite',
            r'deadline'
        ]
        features.deadline_mentions = sum(len(re.findall(pattern, text_lower)) for pattern in deadline_patterns)
        
        # Legal persons
        legal_person_terms = ['advogado', 'procurador', 'curador', 'inventariante', 'leiloeiro']
        features.legal_persons = sum(text_lower.count(term) for term in legal_person_terms)
        
        return features
    
    def _extract_financial_features(self, features: EnhancedFeatureSet, text: str) -> EnhancedFeatureSet:
        """Extract enhanced financial features"""
        
        # Find all currency amounts
        amounts = []
        for pattern in self.financial_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract numeric value
                numeric_part = re.findall(r'[\d.,]+', match)
                for num_str in numeric_part:
                    try:
                        # Convert Brazilian format to float
                        clean_num = num_str.replace('.', '').replace(',', '.')
                        value = float(clean_num)
                        if value > 100:  # Filter out very small values
                            amounts.append(value)
                    except ValueError:
                        continue
        
        # Calculate financial statistics
        features.currency_mentions = len(amounts)
        if amounts:
            features.max_amount = max(amounts)
            features.min_amount = min(amounts)
            features.avg_amount = sum(amounts) / len(amounts)
            features.amount_variance = np.var(amounts) if len(amounts) > 1 else 0.0
        
        # Tax mentions
        tax_terms = ['iptu', 'itbi', 'taxa', 'imposto', 'tributo']
        features.tax_mentions = sum(text.lower().count(term) for term in tax_terms)
        
        # Debt indicators
        debt_terms = ['dívida', 'débito', 'pendência', 'inadimpl', 'mora', 'atraso']
        features.debt_indicators = sum(text.lower().count(term) for term in debt_terms)
        
        # Payment terms
        payment_terms = ['parcelado', 'à vista', 'financiamento', 'prestação', 'entrada']
        features.payment_terms = sum(text.lower().count(term) for term in payment_terms)
        
        return features
    
    def _extract_structure_features(self, features: EnhancedFeatureSet, text: str) -> EnhancedFeatureSet:
        """Analyze document structure"""
        
        # Check for header/footer patterns
        lines = text.split('\n')
        if lines:
            # Header detection (first few lines)
            header_indicators = ['tribunal', 'vara', 'edital', 'poder judiciário']
            features.has_header = any(indicator in lines[0].lower() for indicator in header_indicators)
            
            # Footer detection (last few lines)
            footer_indicators = ['página', 'folha', 'assinatura', 'cartório']
            features.has_footer = any(indicator in lines[-1].lower() for indicator in footer_indicators)
        
        # Table detection
        table_indicators = ['┌', '┐', '└', '┘', '├', '┤', '|', '+---', '===']
        features.has_tables = any(indicator in text for indicator in table_indicators)
        
        # Paragraph structure assessment
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            # Good structure: paragraphs between 20-100 words
            features.paragraph_structure_score = max(0, min(100, 
                100 - abs(avg_paragraph_length - 60) * 2))
        
        # Section organization (headers, numbering)
        section_patterns = [
            r'\d+\.\s+[A-Z]',  # 1. SECTION
            r'[A-Z]+\s*-\s*[A-Z]',  # SECTION - TITLE
            r'\n[A-Z\s]{5,}\n'  # ALL CAPS HEADERS
        ]
        section_count = sum(len(re.findall(pattern, text)) for pattern in section_patterns)
        features.section_organization_score = min(100, section_count * 20)
        
        return features
    
    def _extract_tfidf_features(self, features: EnhancedFeatureSet, text: str) -> EnhancedFeatureSet:
        """Extract TF-IDF features for legal domain"""
        try:
            # Transform text to TF-IDF vector
            tfidf_vector = self.tfidf_vectorizer.fit_transform([text])
            
            if tfidf_vector.shape[1] > 0:
                # Calculate domain-specific TF-IDF scores
                vector_array = tfidf_vector.toarray()[0]
                
                # Legal terms score (first 1/3 of vocabulary)
                legal_end = len(self.legal_vocabulary) // 3
                features.legal_tfidf_score = float(np.sum(vector_array[:legal_end]))
                
                # Financial terms score (middle 1/3)
                financial_start = legal_end
                financial_end = 2 * legal_end
                features.financial_tfidf_score = float(np.sum(vector_array[financial_start:financial_end]))
                
                # Procedural terms score (last 1/3)
                features.procedural_tfidf_score = float(np.sum(vector_array[financial_end:]))
                
        except Exception as e:
            logger.warning(f"TF-IDF extraction failed: {e}")
            
        return features
    
    def _extract_ngram_features(self, features: EnhancedFeatureSet, text: str) -> EnhancedFeatureSet:
        """Extract n-gram features for legal phrases"""
        text_lower = text.lower()
        
        # Count legal bigrams
        features.legal_bigrams = sum(
            text_lower.count(bigram) for bigram in self.legal_ngrams['bigrams']
        )
        
        # Count legal trigrams
        features.legal_trigrams = sum(
            text_lower.count(trigram) for trigram in self.legal_ngrams['trigrams']
        )
        
        # Count judicial phrases
        features.judicial_phrases = sum(
            text_lower.count(phrase) for phrase in self.legal_ngrams['judicial_phrases']
        )
        
        return features
    
    def _extract_risk_features(self, features: EnhancedFeatureSet, text: str) -> EnhancedFeatureSet:
        """Extract risk assessment features"""
        text_lower = text.lower()
        
        # Count risk patterns
        features.high_risk_patterns = sum(
            text_lower.count(pattern) for pattern in self.risk_patterns['high_risk']
        )
        
        features.medium_risk_patterns = sum(
            text_lower.count(pattern) for pattern in self.risk_patterns['medium_risk']
        )
        
        features.low_risk_patterns = sum(
            text_lower.count(pattern) for pattern in self.risk_patterns['low_risk']
        )
        
        features.risk_mitigation_mentions = sum(
            text_lower.count(pattern) for pattern in self.risk_patterns['mitigation']
        )
        
        return features
    
    def _assess_document_quality(self, features: EnhancedFeatureSet, text: str) -> EnhancedFeatureSet:
        """Assess overall document quality"""
        
        # Completeness score (based on essential information presence)
        essential_patterns = [
            r'R\$\s*\d+',  # Financial amounts
            r'\d{7}-\d{2}\.\d{4}',  # Process numbers
            r'leilão|hasta|arrematação',  # Auction terms
            r'imóvel|propriedade|terreno',  # Property terms
        ]
        
        found_patterns = sum(1 for pattern in essential_patterns 
                           if re.search(pattern, text, re.IGNORECASE))
        features.completeness_score = (found_patterns / len(essential_patterns)) * 100
        
        # Clarity score (based on readability and structure)
        clarity_factors = [
            features.avg_sentence_length < 25,  # Not too long sentences
            features.paragraph_structure_score > 50,  # Good paragraph structure
            features.section_organization_score > 30,  # Some organization
            features.punctuation_density > 0.02,  # Proper punctuation
        ]
        
        features.clarity_score = (sum(clarity_factors) / len(clarity_factors)) * 100
        
        # Information density (useful information per unit of text)
        total_entities = (features.currency_mentions + features.legal_bigrams + 
                         features.court_references + features.processo_numbers)
        if features.word_count > 0:
            features.information_density = (total_entities / features.word_count) * 1000
        
        return features
    
    def _calculate_derived_features(self, features: EnhancedFeatureSet) -> EnhancedFeatureSet:
        """Calculate derived intelligence features"""
        
        # Investment attractiveness score
        positive_factors = [
            features.currency_mentions > 0,  # Has financial info
            features.low_risk_patterns > features.high_risk_patterns,  # More positive than negative
            features.completeness_score > 70,  # Complete information
            features.legal_bigrams > 2,  # Proper legal terminology
        ]
        
        negative_factors = [
            features.high_risk_patterns > 2,  # Many risk indicators
            features.debt_indicators > 3,  # Many debt mentions
            features.completeness_score < 50,  # Incomplete information
        ]
        
        attractiveness = sum(positive_factors) * 25 - sum(negative_factors) * 15
        features.investment_attractiveness = max(0, min(100, attractiveness))
        
        # Legal complexity score
        complexity_indicators = [
            features.cpc_references,
            features.lei_references, 
            features.legal_trigrams,
            features.court_references
        ]
        features.legal_complexity_score = min(100, sum(complexity_indicators) * 5)
        
        # Processing difficulty score
        difficulty_factors = [
            features.completeness_score < 60,  # Incomplete info
            features.clarity_score < 50,  # Poor clarity
            features.high_risk_patterns > 1,  # Risk factors present
            features.information_density < 5,  # Low information density
        ]
        features.processing_difficulty = sum(difficulty_factors) * 25
        
        # Urgency score (based on deadlines and temporal references)
        urgency_factors = [
            features.deadline_mentions * 20,
            min(30, features.temporal_references * 10)
        ]
        features.urgency_score = min(100, sum(urgency_factors))
        
        # Extraction confidence (based on quality indicators)
        confidence_factors = [
            features.completeness_score * 0.4,
            features.clarity_score * 0.3,
            features.information_density * 2,  # Scale to 0-100
            min(100, features.legal_bigrams * 10)
        ]
        features.extraction_confidence = min(100, sum(confidence_factors) / len(confidence_factors))
        
        return features
    
    def features_to_dict(self, features: EnhancedFeatureSet) -> Dict[str, Any]:
        """Convert features to dictionary for ML model input"""
        return asdict(features)
    
    def get_feature_importance_names(self) -> List[str]:
        """Get list of feature names for model training"""
        sample_features = EnhancedFeatureSet(job_id="sample")
        return list(asdict(sample_features).keys())

# Global instance for easy import
enhanced_feature_extractor = EnhancedFeatureExtractor()