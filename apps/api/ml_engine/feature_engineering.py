"""
Feature Engineering Module - Etapa 5
Extração e engenharia de features para modelos de ML de lead scoring
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import re

try:
    from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn não disponível - features básicas apenas")

logger = logging.getLogger(__name__)

@dataclass
class FeatureSet:
    """Conjunto de features extraído de um documento"""
    # Identificadores
    job_id: str
    page_number: int
    document_id: Optional[str] = None
    
    # Features de texto básicas
    text_length: int = 0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    
    # Features linguísticas
    language: str = "unknown"
    language_confidence: float = 0.0
    readability_score: float = 0.0
    
    # Features de entidades
    entity_count: int = 0
    cnpj_count: int = 0
    cpf_count: int = 0
    phone_count: int = 0
    email_count: int = 0
    money_count: int = 0
    company_count: int = 0
    
    # Features financeiras
    has_financial_values: bool = False
    max_financial_value: float = 0.0
    total_financial_value: float = 0.0
    financial_keywords_count: int = 0
    
    # Features de urgência
    urgency_score: float = 0.0
    deadline_mentioned: bool = False
    urgency_keywords_count: int = 0
    
    # Features específicas de leilão judicial
    judicial_auction_score: float = 0.0
    legal_notifications_count: int = 0
    property_valuation_indicators: int = 0
    property_status_score: float = 0.0
    legal_compliance_score: float = 0.0
    legal_restrictions_count: int = 0
    
    # Features de risco de investimento
    investment_viability_score: float = 0.0
    risk_level_score: float = 0.0
    legal_authority_mentions: int = 0
    
    # Features de oportunidade imobiliária
    property_discount_indicators: int = 0
    market_value_mentions: int = 0
    auction_urgency_score: float = 0.0
    
    # Features de embedding
    embedding_dimension: int = 0
    embedding_norm: float = 0.0
    embedding_entropy: float = 0.0
    
    # Features derivadas
    text_density: float = 0.0  # entidades por palavra
    financial_density: float = 0.0  # valores por texto
    contact_completeness: float = 0.0  # % de contatos disponíveis
    
    # Score original
    original_lead_score: float = 0.0
    
    # Metadados
    created_at: str = ""
    processing_time: float = 0.0

class FeatureEngineer:
    """Engine de engenharia de features para ML"""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_stats = {}
        self.business_keywords = self._load_business_keywords()
        
        logger.info("FeatureEngineer inicializado")
    
    def _load_business_keywords(self) -> Dict[str, List[str]]:
        """Carrega keywords categorizadas para feature engineering de leilões judiciais"""
        return {
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
    
    def extract_features(self, 
                        text_analysis: Dict[str, Any],
                        embedding_data: Optional[Dict[str, Any]] = None,
                        job_metadata: Optional[Dict[str, Any]] = None) -> FeatureSet:
        """
        Extrai features completo de uma análise de texto
        
        Args:
            text_analysis: Dados da análise de texto
            embedding_data: Dados do embedding (opcional)
            job_metadata: Metadados do job (opcional)
            
        Returns:
            FeatureSet com todas as features extraídas
        """
        start_time = datetime.now()
        
        try:
            # Extrair dados básicos
            text = text_analysis.get('cleaned_text', text_analysis.get('original_text', ''))
            entities = text_analysis.get('entities', [])
            lead_indicators = text_analysis.get('lead_indicators', {})
            
            # Inicializar feature set
            features = FeatureSet(
                job_id=text_analysis.get('job_id', ''),
                page_number=text_analysis.get('page_number', 0),
                created_at=datetime.now().isoformat()
            )
            
            # Features de texto básicas
            features.text_length = len(text)
            features.word_count = len(text.split())
            features.sentence_count = len(text.split('.'))
            features.paragraph_count = len(text.split('\n\n'))
            
            # Features linguísticas
            features.language = text_analysis.get('detected_language', 'unknown')
            features.language_confidence = text_analysis.get('language_confidence', 0.0)
            features.readability_score = self._calculate_readability(text)
            
            # Features de entidades
            features.entity_count = len(entities)
            features = self._extract_entity_features(features, entities)
            
            # Features financeiras
            features = self._extract_financial_features(features, entities, text)
            
            # Features de urgência
            features = self._extract_urgency_features(features, text)
            
            # Features específicas de leilão judicial
            features = self._extract_judicial_auction_features(features, text)
            
            # Features de conformidade legal
            features = self._extract_legal_compliance_features(features, text)
            
            # Features de autoridades legais
            features = self._extract_legal_authority_features(features, text)
            
            # Features de oportunidade imobiliária
            features = self._extract_property_opportunity_features(features, text)
            
            # Features de embedding
            if embedding_data:
                features = self._extract_embedding_features(features, embedding_data)
            
            # Features derivadas
            features = self._calculate_derived_features(features)
            
            # Score original
            features.original_lead_score = lead_indicators.get('lead_score', 0.0)
            
            # Tempo de processamento
            features.processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.debug(f"Features extraídas para {features.job_id}: {features.entity_count} entidades, "
                        f"score {features.original_lead_score}")
            
            return features
            
        except Exception as e:
            logger.error(f"Erro na extração de features: {e}")
            # Retornar features básico em caso de erro
            return FeatureSet(
                job_id=text_analysis.get('job_id', ''),
                page_number=text_analysis.get('page_number', 0),
                created_at=datetime.now().isoformat(),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _extract_entity_features(self, features: FeatureSet, entities: List[Dict]) -> FeatureSet:
        """Extrai features baseadas em entidades"""
        entity_counts = {}
        
        for entity in entities:
            entity_type = entity.get('entity_type', 'unknown')
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        features.cnpj_count = entity_counts.get('cnpj', 0)
        features.cpf_count = entity_counts.get('cpf', 0)
        features.phone_count = entity_counts.get('phone', 0)
        features.email_count = entity_counts.get('email', 0)
        features.money_count = entity_counts.get('money', 0)
        features.company_count = entity_counts.get('company_suffix', 0)
        
        return features
    
    def _extract_financial_features(self, features: FeatureSet, entities: List[Dict], text: str) -> FeatureSet:
        """Extrai features financeiras"""
        money_entities = [e for e in entities if e.get('entity_type') == 'money']
        
        features.has_financial_values = len(money_entities) > 0
        features.financial_keywords_count = self._count_keywords(text, self.business_keywords['financial_data'])
        
        if money_entities:
            # Extrair valores numéricos
            values = []
            for entity in money_entities:
                value_text = entity.get('text', '')
                # Extrair números do texto (R$ 250.000,00 -> 250000)
                numbers = re.findall(r'[\d.,]+', value_text)
                for num_str in numbers:
                    try:
                        # Converter para float (remover pontos de milhares, usar vírgula como decimal)
                        num_str = num_str.replace('.', '').replace(',', '.')
                        value = float(num_str)
                        if value > 100:  # Filtrar valores muito pequenos (provavelmente não são dinheiro)
                            values.append(value)
                    except:
                        continue
            
            if values:
                features.max_financial_value = max(values)
                features.total_financial_value = sum(values)
        
        return features
    
    def _extract_urgency_features(self, features: FeatureSet, text: str) -> FeatureSet:
        """Extrai features de urgência"""
        urgency_keywords = self.business_keywords['urgency_indicators']
        features.urgency_keywords_count = self._count_keywords(text, urgency_keywords)
        
        # Detectar menções de deadline
        deadline_patterns = [
            r'\d+\s+(?:dias?|semanas?|meses?|anos?)',
            r'até\s+\d+',
            r'prazo\s+de\s+\d+',
            r'deadline',
            r'vencimento'
        ]
        
        features.deadline_mentioned = any(re.search(pattern, text.lower()) for pattern in deadline_patterns)
        
        # Calcular score de urgência
        features.urgency_score = min(100, (features.urgency_keywords_count * 20) + 
                                   (30 if features.deadline_mentioned else 0))
        
        return features
    
    def _extract_legal_authority_features(self, features: FeatureSet, text: str) -> FeatureSet:
        """Extrai features de autoridades legais"""
        authority_keywords = self.business_keywords['decision_authorities']
        features.legal_authority_mentions = self._count_keywords(text, authority_keywords)
        
        # Indicadores de procedimentos legais
        legal_procedure_patterns = [
            'procedimento legal', 'rito processual', 'devido processo',
            'competência', 'jurisdição', 'instância', 'recurso'
        ]
        
        legal_procedure_count = sum(
            1 for pattern in legal_procedure_patterns 
            if pattern in text.lower()
        )
        
        # Score de conformidade legal baseado em autoridades mencionadas
        features.legal_compliance_score += min(25, features.legal_authority_mentions * 5)
        
        return features
    

    
    def _extract_embedding_features(self, features: FeatureSet, embedding_data: Dict[str, Any]) -> FeatureSet:
        """Extrai features dos embeddings"""
        vector = embedding_data.get('vector', [])
        
        if vector:
            features.embedding_dimension = len(vector)
            
            # Calcular norma do vetor
            if SKLEARN_AVAILABLE:
                vector_array = np.array(vector)
                features.embedding_norm = float(np.linalg.norm(vector_array))
                
                # Calcular entropia aproximada
                # Entropia mede a "informação" no embedding
                abs_vector = np.abs(vector_array)
                if abs_vector.sum() > 0:
                    prob_dist = abs_vector / abs_vector.sum()
                    prob_dist = prob_dist[prob_dist > 0]  # Remover zeros
                    features.embedding_entropy = float(-np.sum(prob_dist * np.log(prob_dist)))
        
        return features
    
    def _calculate_derived_features(self, features: FeatureSet) -> FeatureSet:
        """Calcula features derivadas"""
        # Densidade de texto (entidades por palavra)
        if features.word_count > 0:
            features.text_density = features.entity_count / features.word_count
        
        # Densidade financeira (valores financeiros por caractere)
        if features.text_length > 0:
            features.financial_density = features.money_count / features.text_length * 1000
        
        # Completude de contato (% de tipos de contato disponíveis)
        contact_types = [features.phone_count, features.email_count, features.cnpj_count]
        available_contacts = sum(1 for count in contact_types if count > 0)
        features.contact_completeness = available_contacts / len(contact_types) * 100
        
        return features
    
    def _calculate_readability(self, text: str) -> float:
        """Calcula score de legibilidade simplificado"""
        if not text:
            return 0.0
        
        words = text.split()
        sentences = text.split('.')
        
        if len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_chars_per_word = sum(len(word) for word in words) / len(words) if words else 0
        
        # Score simplificado (quanto menor, mais legível)
        readability = (avg_words_per_sentence * 1.5) + (avg_chars_per_word * 2)
        
        # Normalizar para 0-100 (100 = mais legível)
        return max(0, min(100, 100 - (readability - 10) * 2))
    
    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        """Conta ocorrências de keywords no texto"""
        text_lower = text.lower()
        count = 0
        
        for keyword in keywords:
            count += text_lower.count(keyword.lower())
        
        return count
    
    def extract_batch_features(self, analyses: List[Dict[str, Any]], 
                             embeddings: Optional[List[Dict[str, Any]]] = None) -> List[FeatureSet]:
        """
        Extrai features em lote para múltiplas análises
        
        Args:
            analyses: Lista de análises de texto
            embeddings: Lista de embeddings correspondentes
            
        Returns:
            Lista de FeatureSets
        """
        features_list = []
        
        for i, analysis in enumerate(analyses):
            embedding_data = embeddings[i] if embeddings and i < len(embeddings) else None
            
            try:
                features = self.extract_features(analysis, embedding_data)
                features_list.append(features)
            except Exception as e:
                logger.error(f"Erro na extração de features do item {i}: {e}")
                continue
        
        logger.info(f"Features extraídas em lote: {len(features_list)} de {len(analyses)} análises")
        return features_list
    
    def features_to_dataframe(self, features_list: List[FeatureSet]) -> 'pd.DataFrame':
        """Converte lista de features para DataFrame do pandas"""
        if not SKLEARN_AVAILABLE:
            logger.error("pandas/sklearn não disponível para DataFrame")
            return None
        
        # Converter para dicionários
        features_dicts = [asdict(features) for features in features_list]
        
        # Criar DataFrame
        df = pd.DataFrame(features_dicts)
        
        # Converter tipos apropriados
        numeric_columns = [
            'text_length', 'word_count', 'sentence_count', 'paragraph_count',
            'language_confidence', 'readability_score', 'entity_count',
            'cnpj_count', 'cpf_count', 'phone_count', 'email_count', 'money_count',
            'company_count', 'max_financial_value', 'total_financial_value',
            'financial_keywords_count', 'urgency_score', 'urgency_keywords_count',
            'judicial_auction_score', 'legal_notifications_count', 'property_valuation_indicators',
            'property_status_score', 'legal_compliance_score', 'legal_restrictions_count',
            'investment_viability_score', 'risk_level_score', 'legal_authority_mentions',
            'property_discount_indicators', 'market_value_mentions', 'auction_urgency_score',
            'embedding_dimension', 'embedding_norm',
            'embedding_entropy', 'text_density', 'financial_density',
            'contact_completeness', 'original_lead_score', 'processing_time'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Converter booleanos
        boolean_columns = ['has_financial_values', 'deadline_mentioned']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        logger.info(f"DataFrame criado: {df.shape[0]} linhas, {df.shape[1]} colunas")
        return df
    
    def get_feature_importance_names(self) -> List[str]:
        """Retorna nomes das features para análise de importância"""
        return [
            'text_length', 'word_count', 'entity_count', 'language_confidence',
            'readability_score', 'cnpj_count', 'phone_count', 'email_count',
            'money_count', 'company_count', 'has_financial_values',
            'max_financial_value', 'total_financial_value', 'financial_keywords_count',
            'urgency_score', 'deadline_mentioned', 'urgency_keywords_count',
            'judicial_auction_score', 'legal_notifications_count', 'property_valuation_indicators',
            'property_status_score', 'legal_compliance_score', 'legal_restrictions_count',
            'investment_viability_score', 'risk_level_score', 'legal_authority_mentions',
            'property_discount_indicators', 'market_value_mentions', 'auction_urgency_score',
            'embedding_dimension', 'embedding_norm', 'embedding_entropy',
            'text_density', 'financial_density', 'contact_completeness'
        ]
    
    def get_feature_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do feature engineering"""
        return {
            'scalers_fitted': len(self.scalers),
            'encoders_fitted': len(self.encoders),
            'feature_categories': len(self.business_keywords),
            'total_keywords': sum(len(words) for words in self.business_keywords.values()),
            'sklearn_available': SKLEARN_AVAILABLE
        }

    def _extract_judicial_auction_features(self, features: FeatureSet, text: str) -> FeatureSet:
        """Extrai features específicas de leilão judicial"""
        # Contagem de indicadores de leilão judicial
        judicial_keywords = self.business_keywords['judicial_auction']
        judicial_count = self._count_keywords(text, judicial_keywords)
        features.judicial_auction_score = min(100, judicial_count * 25)
        
        # Notificações legais
        notification_keywords = self.business_keywords['legal_notifications']
        features.legal_notifications_count = self._count_keywords(text, notification_keywords)
        
        # Indicadores de avaliação de propriedade
        valuation_keywords = self.business_keywords['property_valuation']
        features.property_valuation_indicators = self._count_keywords(text, valuation_keywords)
        
        # Score de status da propriedade
        property_status_keywords = self.business_keywords['property_status']
        property_status_count = self._count_keywords(text, property_status_keywords)
        
        # Verificar se é status positivo (livre) ou negativo (ocupado)
        positive_status = ['desocupado', 'livre', 'vago', 'desembaraçado', 'sem ocupantes']
        negative_status = ['inquilino', 'locatário', 'posseiro', 'ocupação irregular']
        
        positive_count = self._count_keywords(text, positive_status)
        negative_count = self._count_keywords(text, negative_status)
        
        # Score positivo se mais indicadores livres, negativo se ocupado
        if positive_count > negative_count:
            features.property_status_score = min(100, positive_count * 30)
        else:
            features.property_status_score = max(-50, -negative_count * 20)
        
        # Restrições legais (quanto mais, pior)
        restriction_keywords = self.business_keywords['legal_restrictions']
        features.legal_restrictions_count = self._count_keywords(text, restriction_keywords)
        
        return features
    
    def _extract_legal_compliance_features(self, features: FeatureSet, text: str) -> FeatureSet:
        """Extrai features de conformidade legal"""
        compliance_keywords = self.business_keywords['legal_compliance']
        compliance_count = self._count_keywords(text, compliance_keywords)
        features.legal_compliance_score = min(100, compliance_count * 20)
        
        # Menções de autoridades legais
        authority_keywords = self.business_keywords['decision_authorities']
        features.legal_authority_mentions = self._count_keywords(text, authority_keywords)
        
        # Calcular score de risco baseado em restrições vs conformidade
        risk_score = features.legal_restrictions_count * 10  # Penalidade por restrições
        compliance_bonus = compliance_count * 5  # Bônus por conformidade
        features.risk_level_score = max(0, min(100, risk_score - compliance_bonus))
        
        return features
    
    def _extract_property_opportunity_features(self, features: FeatureSet, text: str) -> FeatureSet:
        """Extrai features de oportunidade imobiliária"""
        opportunity_keywords = self.business_keywords['investment_opportunity']
        opportunity_count = self._count_keywords(text, opportunity_keywords)
        features.investment_viability_score = min(100, opportunity_count * 15)
        
        # Indicadores de desconto/preço baixo
        discount_patterns = [
            'abaixo do mercado', 'desconto', 'barganha', 'oportunidade',
            '50%', 'metade', 'menor preço', 'lance mínimo'
        ]
        features.property_discount_indicators = self._count_keywords(text, discount_patterns)
        
        # Menções de valor de mercado
        market_value_patterns = [
            'valor de mercado', 'avaliação', 'preço de mercado',
            'valor venal', 'valor da avaliação'
        ]
        features.market_value_mentions = self._count_keywords(text, market_value_patterns)
        
        # Score de urgência do leilão
        urgency_keywords = self.business_keywords['urgency_indicators']
        urgency_count = self._count_keywords(text, urgency_keywords)
        features.auction_urgency_score = min(100, urgency_count * 20)
        
        return features

# Instância global do feature engineer
feature_engineer = FeatureEngineer() 