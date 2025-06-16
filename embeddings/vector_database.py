"""
Vector Database Manager - Etapa 4
Gerenciamento de banco de dados vectorial para busca semântica
"""

import os
import json
import logging
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid

# Vector storage libraries
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS não disponível - usando busca linear")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy não disponível")

logger = logging.getLogger(__name__)

@dataclass
class VectorDocument:
    """Documento com embedding para armazenamento"""
    id: str
    text: str
    vector: List[float]
    metadata: Dict[str, Any]
    created_at: str
    job_id: Optional[str] = None
    page_number: Optional[int] = None
    lead_score: Optional[float] = None

@dataclass
class SearchResult:
    """Resultado de busca no banco vectorial"""
    document: VectorDocument
    similarity: float
    rank: int

class VectorDatabase:
    """Banco de dados vectorial com busca por similaridade"""
    
    def __init__(self, 
                 storage_path: str = "storage/vectors",
                 index_type: str = "flat"):
        """
        Inicializa o banco de dados vectorial
        
        Args:
            storage_path: Caminho para armazenamento
            index_type: Tipo de índice ('flat', 'ivf', 'hnsw')
        """
        self.storage_path = storage_path
        self.index_type = index_type
        self.documents = {}  # id -> VectorDocument
        self.index = None
        self.vector_dimension = None
        self.id_to_index = {}  # mapping document_id -> index position
        self.index_to_id = {}  # mapping index position -> document_id
        
        # Criar diretório de storage
        os.makedirs(storage_path, exist_ok=True)
        
        # Carregar dados existentes
        self._load_from_disk()
        
        logger.info(f"VectorDatabase inicializado - Documentos: {len(self.documents)}, "
                   f"Dimensão: {self.vector_dimension}, Índice: {self.index_type}")
    
    def add_document(self, 
                    text: str, 
                    vector: List[float], 
                    metadata: Dict[str, Any] = None,
                    job_id: str = None,
                    page_number: int = None,
                    lead_score: float = None) -> str:
        """
        Adiciona documento ao banco vectorial
        
        Args:
            text: Texto do documento
            vector: Embedding do texto
            metadata: Metadados adicionais
            job_id: ID do job relacionado
            page_number: Número da página
            lead_score: Score de lead
            
        Returns:
            ID do documento criado
        """
        try:
            # Gerar ID único
            doc_id = str(uuid.uuid4())
            
            # Validar dimensão do vetor
            if self.vector_dimension is None:
                self.vector_dimension = len(vector)
                logger.info(f"Dimensão do vetor definida: {self.vector_dimension}")
            elif len(vector) != self.vector_dimension:
                raise ValueError(f"Dimensão do vetor incorreta: {len(vector)} != {self.vector_dimension}")
            
            # Criar documento
            document = VectorDocument(
                id=doc_id,
                text=text,
                vector=vector,
                metadata=metadata or {},
                created_at=datetime.now().isoformat(),
                job_id=job_id,
                page_number=page_number,
                lead_score=lead_score
            )
            
            # Adicionar aos documentos
            self.documents[doc_id] = document
            
            # Atualizar índice
            self._add_to_index(doc_id, vector)
            
            # Salvar no disco
            self._save_to_disk()
            
            logger.debug(f"Documento adicionado: {doc_id} - {len(text)} chars")
            return doc_id
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documento: {e}")
            raise
    
    def search_similar(self, 
                      query_vector: List[float], 
                      k: int = 10,
                      threshold: float = 0.0) -> List[SearchResult]:
        """
        Busca documentos similares
        
        Args:
            query_vector: Vetor da query
            k: Número de resultados
            threshold: Threshold mínimo de similaridade
            
        Returns:
            Lista de resultados ordenados por similaridade
        """
        try:
            if not self.documents:
                return []
            
            if len(query_vector) != self.vector_dimension:
                raise ValueError(f"Dimensão da query incorreta: {len(query_vector)} != {self.vector_dimension}")
            
            results = []
            
            if FAISS_AVAILABLE and self.index is not None and NUMPY_AVAILABLE:
                # Busca com FAISS
                query_array = np.array([query_vector], dtype=np.float32)
                distances, indices = self.index.search(query_array, min(k, len(self.documents)))
                
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx == -1:  # FAISS retorna -1 para posições vazias
                        continue
                    
                    # Converter distância para similaridade coseno
                    similarity = 1.0 - distance if distance <= 1.0 else 0.0
                    
                    if similarity >= threshold:
                        doc_id = self.index_to_id.get(idx)
                        if doc_id and doc_id in self.documents:
                            result = SearchResult(
                                document=self.documents[doc_id],
                                similarity=similarity,
                                rank=i + 1
                            )
                            results.append(result)
            
            else:
                # Busca linear (fallback)
                similarities = []
                
                for doc_id, document in self.documents.items():
                    similarity = self._calculate_cosine_similarity(query_vector, document.vector)
                    
                    if similarity >= threshold:
                        similarities.append((doc_id, similarity))
                
                # Ordenar por similaridade (maior primeiro)
                similarities.sort(key=lambda x: x[1], reverse=True)
                
                # Limitar resultados
                similarities = similarities[:k]
                
                # Criar resultados
                for i, (doc_id, similarity) in enumerate(similarities):
                    result = SearchResult(
                        document=self.documents[doc_id],
                        similarity=similarity,
                        rank=i + 1
                    )
                    results.append(result)
            
            logger.debug(f"Busca concluída: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []
    
    def search_by_job(self, job_id: str) -> List[VectorDocument]:
        """Busca documentos por job ID"""
        return [doc for doc in self.documents.values() if doc.job_id == job_id]
    
    def search_by_lead_score(self, min_score: float) -> List[VectorDocument]:
        """Busca documentos por score de lead mínimo"""
        results = []
        for doc in self.documents.values():
            if doc.lead_score is not None and doc.lead_score >= min_score:
                results.append(doc)
        
        # Ordenar por score (maior primeiro)
        results.sort(key=lambda x: x.lead_score or 0, reverse=True)
        return results
    
    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Obtém documento por ID"""
        return self.documents.get(doc_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """Remove documento do banco"""
        try:
            if doc_id not in self.documents:
                return False
            
            # Remover do índice
            self._remove_from_index(doc_id)
            
            # Remover dos documentos
            del self.documents[doc_id]
            
            # Salvar no disco
            self._save_to_disk()
            
            logger.debug(f"Documento removido: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover documento {doc_id}: {e}")
            return False
    
    def delete_job_documents(self, job_id: str) -> int:
        """Remove todos os documentos de um job"""
        doc_ids_to_remove = [doc_id for doc_id, doc in self.documents.items() if doc.job_id == job_id]
        
        removed_count = 0
        for doc_id in doc_ids_to_remove:
            if self.delete_document(doc_id):
                removed_count += 1
        
        logger.info(f"Documentos do job {job_id} removidos: {removed_count}")
        return removed_count
    
    def _add_to_index(self, doc_id: str, vector: List[float]):
        """Adiciona vetor ao índice"""
        try:
            if FAISS_AVAILABLE and NUMPY_AVAILABLE:
                vector_array = np.array([vector], dtype=np.float32)
                
                if self.index is None:
                    # Criar índice
                    if self.index_type == "flat":
                        self.index = faiss.IndexFlatIP(self.vector_dimension)  # Inner Product (cosine for normalized vectors)
                    elif self.index_type == "ivf":
                        quantizer = faiss.IndexFlatIP(self.vector_dimension)
                        self.index = faiss.IndexIVFFlat(quantizer, self.vector_dimension, min(100, max(1, len(self.documents) // 10)))
                    else:
                        # Default to flat
                        self.index = faiss.IndexFlatIP(self.vector_dimension)
                
                # Normalizar vetor para busca coseno
                faiss.normalize_L2(vector_array)
                
                # Adicionar ao índice
                current_index = self.index.ntotal
                self.index.add(vector_array)
                
                # Mapear ID para índice
                self.id_to_index[doc_id] = current_index
                self.index_to_id[current_index] = doc_id
                
                logger.debug(f"Vetor adicionado ao índice FAISS: posição {current_index}")
            
        except Exception as e:
            logger.warning(f"Erro ao adicionar ao índice FAISS: {e}")
    
    def _remove_from_index(self, doc_id: str):
        """Remove vetor do índice (recria índice se necessário)"""
        try:
            if doc_id in self.id_to_index:
                # Para FAISS, é mais eficiente recriar o índice
                self._rebuild_index()
                
        except Exception as e:
            logger.warning(f"Erro ao remover do índice: {e}")
    
    def _rebuild_index(self):
        """Reconstrói o índice FAISS"""
        try:
            if not FAISS_AVAILABLE or not NUMPY_AVAILABLE:
                return
            
            self.index = None
            self.id_to_index.clear()
            self.index_to_id.clear()
            
            # Readicionar todos os documentos
            for doc_id, document in self.documents.items():
                self._add_to_index(doc_id, document.vector)
            
            logger.info(f"Índice FAISS reconstruído: {len(self.documents)} documentos")
            
        except Exception as e:
            logger.error(f"Erro ao reconstruir índice: {e}")
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade coseno entre dois vetores"""
        try:
            if NUMPY_AVAILABLE:
                v1 = np.array(vec1)
                v2 = np.array(vec2)
                
                dot_product = np.dot(v1, v2)
                norm1 = np.linalg.norm(v1)
                norm2 = np.linalg.norm(v2)
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                return float(dot_product / (norm1 * norm2))
            
            else:
                # Implementação manual
                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                norm1 = sum(a * a for a in vec1) ** 0.5
                norm2 = sum(b * b for b in vec2) ** 0.5
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                return dot_product / (norm1 * norm2)
                
        except Exception as e:
            logger.error(f"Erro no cálculo de similaridade: {e}")
            return 0.0
    
    def _save_to_disk(self):
        """Salva dados no disco"""
        try:
            # Salvar documentos
            documents_file = os.path.join(self.storage_path, "documents.json")
            
            # Converter documentos para JSON
            documents_dict = {}
            for doc_id, document in self.documents.items():
                documents_dict[doc_id] = asdict(document)
            
            with open(documents_file, 'w', encoding='utf-8') as f:
                json.dump(documents_dict, f, ensure_ascii=False, indent=2)
            
            # Salvar metadados
            metadata_file = os.path.join(self.storage_path, "metadata.json")
            metadata = {
                'vector_dimension': self.vector_dimension,
                'index_type': self.index_type,
                'document_count': len(self.documents),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # Salvar índice FAISS se disponível
            if FAISS_AVAILABLE and self.index is not None:
                index_file = os.path.join(self.storage_path, "faiss_index.index")
                faiss.write_index(self.index, index_file)
                
                # Salvar mapeamentos
                mappings_file = os.path.join(self.storage_path, "mappings.pkl")
                mappings = {
                    'id_to_index': self.id_to_index,
                    'index_to_id': self.index_to_id
                }
                
                with open(mappings_file, 'wb') as f:
                    pickle.dump(mappings, f)
            
            logger.debug(f"Dados salvos no disco: {len(self.documents)} documentos")
            
        except Exception as e:
            logger.error(f"Erro ao salvar no disco: {e}")
    
    def _load_from_disk(self):
        """Carrega dados do disco"""
        try:
            documents_file = os.path.join(self.storage_path, "documents.json")
            
            if os.path.exists(documents_file):
                with open(documents_file, 'r', encoding='utf-8') as f:
                    documents_dict = json.load(f)
                
                # Converter de dict para VectorDocument
                for doc_id, doc_data in documents_dict.items():
                    document = VectorDocument(**doc_data)
                    self.documents[doc_id] = document
                
                logger.info(f"Documentos carregados: {len(self.documents)}")
            
            # Carregar metadados
            metadata_file = os.path.join(self.storage_path, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                self.vector_dimension = metadata.get('vector_dimension')
                logger.info(f"Metadados carregados - Dimensão: {self.vector_dimension}")
            
            # Carregar índice FAISS
            if FAISS_AVAILABLE and self.vector_dimension:
                index_file = os.path.join(self.storage_path, "faiss_index.index")
                mappings_file = os.path.join(self.storage_path, "mappings.pkl")
                
                if os.path.exists(index_file) and os.path.exists(mappings_file):
                    try:
                        self.index = faiss.read_index(index_file)
                        
                        with open(mappings_file, 'rb') as f:
                            mappings = pickle.load(f)
                        
                        self.id_to_index = mappings.get('id_to_index', {})
                        self.index_to_id = mappings.get('index_to_id', {})
                        
                        logger.info(f"Índice FAISS carregado: {self.index.ntotal} vetores")
                    except Exception as e:
                        logger.warning(f"Erro ao carregar índice FAISS: {e}")
                        self._rebuild_index()
                else:
                    # Reconstruir índice se não existir
                    if self.documents:
                        self._rebuild_index()
            
        except Exception as e:
            logger.error(f"Erro ao carregar do disco: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco vectorial"""
        lead_scores = [doc.lead_score for doc in self.documents.values() if doc.lead_score is not None]
        
        stats = {
            'total_documents': len(self.documents),
            'vector_dimension': self.vector_dimension,
            'index_type': self.index_type,
            'faiss_available': FAISS_AVAILABLE,
            'index_built': self.index is not None,
            'documents_with_lead_scores': len(lead_scores),
            'average_lead_score': sum(lead_scores) / len(lead_scores) if lead_scores else 0,
            'max_lead_score': max(lead_scores) if lead_scores else 0,
            'jobs_count': len(set(doc.job_id for doc in self.documents.values() if doc.job_id))
        }
        
        return stats
    
    def clear_all(self):
        """Limpa todo o banco de dados"""
        self.documents.clear()
        self.index = None
        self.id_to_index.clear()
        self.index_to_id.clear()
        self.vector_dimension = None
        
        # Remover arquivos do disco
        try:
            import shutil
            if os.path.exists(self.storage_path):
                shutil.rmtree(self.storage_path)
                os.makedirs(self.storage_path, exist_ok=True)
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos: {e}")
        
        logger.info("Banco vectorial limpo")

# Instância global do banco vectorial
vector_db = VectorDatabase() 