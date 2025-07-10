"""
Embeddings Engine - Etapa 4
Geração de embeddings e operações vectoriais para busca semântica
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from dataclasses import dataclass, asdict

# Embeddings libraries
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers não disponível - usando embeddings básicos")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn não disponível")

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Resultado da geração de embeddings"""
    text: str
    vector: List[float]
    model_name: str
    vector_dimension: int
    created_at: str
    metadata: Dict[str, Any]

@dataclass
class SimilarityResult:
    """Resultado de busca por similaridade"""
    query_text: str
    matches: List[Dict[str, Any]]
    total_matches: int
    search_time: float
    threshold_used: float

class EmbeddingEngine:
    """Engine principal para geração e busca de embeddings"""
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 use_gpu: bool = False):
        """
        Inicializa o engine de embeddings
        
        Args:
            model_name: Nome do modelo a usar
            use_gpu: Se deve usar GPU (quando disponível)
        """
        self.model_name = model_name
        self.use_gpu = use_gpu
        self.model = None
        self.tfidf_vectorizer = None
        self.vector_cache = {}
        
        # Inicializar modelo
        self._initialize_model()
        
        logger.info(f"EmbeddingEngine inicializado - Modelo: {self.model_name}")
    
    def _initialize_model(self):
        """Inicializa o modelo de embeddings"""
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                # Tentar usar SentenceTransformers (melhor qualidade)
                device = 'cuda' if self.use_gpu else 'cpu'
                
                # Modelos recomendados para português e inglês
                model_options = [
                    "neuralmind/bert-base-portuguese-cased",  # Português específico
                    "sentence-transformers/all-MiniLM-L6-v2",  # Multilingual, rápido
                    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # Multilingual, qualidade
                    "all-MiniLM-L6-v2"  # Fallback
                ]
                
                for model_option in model_options:
                    try:
                        self.model = SentenceTransformer(model_option, device=device)
                        self.model_name = model_option
                        logger.info(f"Modelo SentenceTransformer carregado: {model_option}")
                        return
                    except Exception as e:
                        logger.warning(f"Falha ao carregar modelo {model_option}: {e}")
                        continue
                
            # Fallback para TF-IDF se SentenceTransformers não disponível
            if SKLEARN_AVAILABLE:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words=None,  # Vamos gerenciar stopwords manualmente
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.8
                )
                self.model_name = "tfidf-sklearn"
                logger.info("Usando TF-IDF como fallback para embeddings")
            else:
                # Último fallback - embeddings básicos
                self.model_name = "basic-bow"
                logger.warning("Usando embeddings básicos (bag-of-words)")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar modelo de embeddings: {e}")
            self.model_name = "basic-bow"
    
    def generate_embedding(self, text: str, metadata: Dict[str, Any] = None) -> EmbeddingResult:
        """
        Gera embedding para um texto
        
        Args:
            text: Texto para gerar embedding
            metadata: Metadados adicionais
            
        Returns:
            Resultado com embedding gerado
        """
        try:
            if not text or len(text.strip()) < 3:
                return self._create_empty_embedding(text, "Texto muito curto")
            
            # Tentar cache primeiro
            text_hash = hash(text)
            if text_hash in self.vector_cache:
                cached_result = self.vector_cache[text_hash]
                logger.debug(f"Embedding do cache usado para texto de {len(text)} caracteres")
                return cached_result
            
            start_time = datetime.now()
            
            # Gerar embedding baseado no modelo disponível
            if self.model and SENTENCE_TRANSFORMERS_AVAILABLE:
                # SentenceTransformers
                vector = self.model.encode(text, convert_to_tensor=False)
                vector = vector.tolist() if hasattr(vector, 'tolist') else list(vector)
                
            elif self.tfidf_vectorizer and SKLEARN_AVAILABLE:
                # TF-IDF
                # Primeiro fit se necessário
                try:
                    vector_sparse = self.tfidf_vectorizer.transform([text])
                except:
                    # Primeiro texto - fazer fit
                    self.tfidf_vectorizer.fit([text])
                    vector_sparse = self.tfidf_vectorizer.transform([text])
                
                vector = vector_sparse.toarray()[0].tolist()
                
            else:
                # Fallback básico - bag of words simples
                vector = self._generate_basic_embedding(text)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Criar resultado
            result = EmbeddingResult(
                text=text,
                vector=vector,
                model_name=self.model_name,
                vector_dimension=len(vector),
                created_at=datetime.now().isoformat(),
                metadata={
                    **(metadata or {}),
                    'processing_time': processing_time,
                    'text_length': len(text),
                    'word_count': len(text.split())
                }
            )
            
            # Cachear resultado
            self.vector_cache[text_hash] = result
            
            logger.debug(f"Embedding gerado: {len(vector)}D para texto de {len(text)} caracteres")
            return result
            
        except Exception as e:
            logger.error(f"Erro na geração de embedding: {e}")
            return self._create_empty_embedding(text, str(e))
    
    def _generate_basic_embedding(self, text: str) -> List[float]:
        """Gera embedding básico usando bag-of-words"""
        # Tokenizar
        words = text.lower().split()
        
        # Vocabulário básico de palavras importantes para negócios
        business_vocab = [
            'empresa', 'negócio', 'projeto', 'contrato', 'oportunidade',
            'tecnologia', 'sistema', 'desenvolvimento', 'investimento',
            'receita', 'lucro', 'crescimento', 'mercado', 'cliente',
            'produto', 'serviço', 'solução', 'digital', 'automação'
        ]
        
        # Criar vetor baseado na presença de palavras do vocabulário
        vector = []
        for vocab_word in business_vocab:
            # Contar ocorrências da palavra
            count = sum(1 for word in words if vocab_word in word)
            vector.append(float(count))
        
        # Adicionar features básicas
        vector.extend([
            float(len(words)),  # Comprimento
            float(len(text)),   # Caracteres
            float(sum(1 for w in words if w.isupper())),  # Palavras maiúsculas
            float(sum(1 for c in text if c.isdigit())),   # Números
        ])
        
        # Normalizar
        vector_sum = sum(vector)
        if vector_sum > 0:
            vector = [v / vector_sum for v in vector]
        
        return vector
    
    def _create_empty_embedding(self, text: str, reason: str) -> EmbeddingResult:
        """Cria embedding vazio em caso de erro"""
        dimension = 384 if "MiniLM" in self.model_name else 100
        return EmbeddingResult(
            text=text,
            vector=[0.0] * dimension,
            model_name=self.model_name,
            vector_dimension=dimension,
            created_at=datetime.now().isoformat(),
            metadata={'error': reason}
        )
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula similaridade coseno entre dois embeddings
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
            
        Returns:
            Similaridade (0.0 a 1.0)
        """
        try:
            if not embedding1 or not embedding2:
                return 0.0
            
            if len(embedding1) != len(embedding2):
                logger.warning("Embeddings com dimensões diferentes")
                return 0.0
            
            # Usar sklearn se disponível
            if SKLEARN_AVAILABLE:
                emb1 = np.array(embedding1).reshape(1, -1)
                emb2 = np.array(embedding2).reshape(1, -1)
                similarity = cosine_similarity(emb1, emb2)[0][0]
                return float(similarity)
            
            # Implementação manual de similaridade coseno
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))  # Clamp entre 0 e 1
            
        except Exception as e:
            logger.error(f"Erro no cálculo de similaridade: {e}")
            return 0.0
    
    def find_similar_texts(self, 
                          query_embedding: List[float], 
                          candidate_embeddings: List[Tuple[str, List[float], Dict[str, Any]]], 
                          threshold: float = 0.7,
                          max_results: int = 10) -> SimilarityResult:
        """
        Encontra textos similares baseado em embeddings
        
        Args:
            query_embedding: Embedding da query
            candidate_embeddings: Lista de (texto, embedding, metadata)
            threshold: Threshold mínimo de similaridade
            max_results: Máximo de resultados
            
        Returns:
            Resultados de similaridade
        """
        start_time = datetime.now()
        
        try:
            similarities = []
            
            for text, embedding, metadata in candidate_embeddings:
                similarity = self.calculate_similarity(query_embedding, embedding)
                
                if similarity >= threshold:
                    similarities.append({
                        'text': text,
                        'similarity': similarity,
                        'metadata': metadata
                    })
            
            # Ordenar por similaridade (maior primeiro)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Limitar resultados
            similarities = similarities[:max_results]
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            return SimilarityResult(
                query_text="",  # Será preenchido pelo chamador
                matches=similarities,
                total_matches=len(similarities),
                search_time=search_time,
                threshold_used=threshold
            )
            
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {e}")
            return SimilarityResult(
                query_text="",
                matches=[],
                total_matches=0,
                search_time=0.0,
                threshold_used=threshold
            )
    
    def batch_generate_embeddings(self, 
                                 texts: List[str], 
                                 batch_size: int = 32) -> List[EmbeddingResult]:
        """
        Gera embeddings em lote para melhor performance
        
        Args:
            texts: Lista de textos
            batch_size: Tamanho do lote
            
        Returns:
            Lista de resultados de embedding
        """
        results = []
        
        try:
            # Processar em lotes
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                if self.model and SENTENCE_TRANSFORMERS_AVAILABLE:
                    # Geração em lote com SentenceTransformers
                    vectors = self.model.encode(batch, convert_to_tensor=False)
                    
                    for j, text in enumerate(batch):
                        vector = vectors[j].tolist() if hasattr(vectors[j], 'tolist') else list(vectors[j])
                        
                        result = EmbeddingResult(
                            text=text,
                            vector=vector,
                            model_name=self.model_name,
                            vector_dimension=len(vector),
                            created_at=datetime.now().isoformat(),
                            metadata={
                                'batch_processed': True,
                                'batch_size': len(batch),
                                'text_length': len(text),
                                'word_count': len(text.split())
                            }
                        )
                        results.append(result)
                else:
                    # Processar individualmente
                    for text in batch:
                        result = self.generate_embedding(text)
                        results.append(result)
                
                logger.debug(f"Lote processado: {len(batch)} embeddings gerados")
            
            logger.info(f"Geração em lote concluída: {len(results)} embeddings gerados")
            return results
            
        except Exception as e:
            logger.error(f"Erro na geração em lote: {e}")
            # Fallback para processamento individual
            return [self.generate_embedding(text) for text in texts]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo atual"""
        info = {
            'model_name': self.model_name,
            'model_available': self.model is not None or self.tfidf_vectorizer is not None,
            'sentence_transformers_available': SENTENCE_TRANSFORMERS_AVAILABLE,
            'sklearn_available': SKLEARN_AVAILABLE,
            'cache_size': len(self.vector_cache),
            'use_gpu': self.use_gpu
        }
        
        if self.model and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Obter dimensão do modelo
                test_embedding = self.model.encode("test", convert_to_tensor=False)
                info['vector_dimension'] = len(test_embedding)
                info['model_type'] = 'SentenceTransformer'
            except:
                info['vector_dimension'] = 'unknown'
                info['model_type'] = 'SentenceTransformer'
        elif self.tfidf_vectorizer:
            info['model_type'] = 'TF-IDF'
            info['vector_dimension'] = getattr(self.tfidf_vectorizer, 'max_features', 1000)
        else:
            info['model_type'] = 'Basic'
            info['vector_dimension'] = 23  # Dimensão do embedding básico
        
        return info
    
    def clear_cache(self):
        """Limpa o cache de embeddings"""
        cache_size = len(self.vector_cache)
        self.vector_cache.clear()
        logger.info(f"Cache limpo: {cache_size} embeddings removidos")

# Instância global do engine
embedding_engine = EmbeddingEngine() 