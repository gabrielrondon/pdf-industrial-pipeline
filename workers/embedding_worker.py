"""
Embedding Worker - Etapa 4
Worker responsável por gerar embeddings dos textos processados
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from embeddings.embedding_engine import embedding_engine, EmbeddingResult
from embeddings.vector_database import vector_db, VectorDocument
from utils.storage_manager import storage_manager

logger = logging.getLogger(__name__)

class EmbeddingWorker:
    """Worker para geração de embeddings e armazenamento vectorial"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
    
    async def process_job_embeddings(self, job_id: str) -> Dict[str, Any]:
        """
        Processa embeddings para todas as análises de texto de um job
        
        Args:
            job_id: ID do job a processar
            
        Returns:
            Resultado do processamento
        """
        logger.info(f"Iniciando processamento de embeddings para job {job_id}")
        
        try:
            # Buscar análises de texto existentes
            text_analyses = self._load_text_analyses(job_id)
            
            if not text_analyses:
                logger.warning(f"Nenhuma análise de texto encontrada para job {job_id}")
                return {
                    'job_id': job_id,
                    'status': 'no_text_analysis',
                    'message': 'Nenhuma análise de texto encontrada',
                    'embeddings_generated': 0
                }
            
            embeddings_generated = 0
            errors = []
            
            # Processar cada análise de texto
            for analysis in text_analyses:
                try:
                    result = await self._process_single_analysis(job_id, analysis)
                    if result:
                        embeddings_generated += 1
                        logger.debug(f"Embedding gerado para página {analysis.get('page_number', '?')}")
                    
                except Exception as e:
                    error_msg = f"Erro na página {analysis.get('page_number', '?')}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    self.error_count += 1
            
            # Salvar estatísticas do processamento
            stats = {
                'job_id': job_id,
                'embeddings_generated': embeddings_generated,
                'errors': errors,
                'processed_at': datetime.now().isoformat(),
                'model_info': embedding_engine.get_model_info(),
                'vector_db_stats': vector_db.get_stats()
            }
            
            # Salvar estatísticas
            await self._save_embedding_stats(job_id, stats)
            
            self.processed_count += embeddings_generated
            
            logger.info(f"✅ Processamento de embeddings concluído para job {job_id}: "
                       f"{embeddings_generated} embeddings gerados, {len(errors)} erros")
            
            return {
                'job_id': job_id,
                'status': 'completed',
                'embeddings_generated': embeddings_generated,
                'errors': errors,
                'model_used': embedding_engine.model_name
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento de embeddings para job {job_id}: {e}")
            self.error_count += 1
            
            return {
                'job_id': job_id,
                'status': 'error',
                'error': str(e),
                'embeddings_generated': 0
            }
    
    async def _process_single_analysis(self, job_id: str, analysis: Dict[str, Any]) -> bool:
        """
        Processa uma única análise de texto para gerar embedding
        
        Args:
            job_id: ID do job
            analysis: Dados da análise de texto
            
        Returns:
            True se processado com sucesso
        """
        try:
            # Extrair texto limpo
            clean_text = analysis.get('cleaned_text', analysis.get('clean_text', ''))
            if not clean_text or len(clean_text.strip()) < 10:
                logger.debug(f"Texto muito curto para gerar embedding: {len(clean_text)} chars")
                return False
            
            # Preparar metadados
            metadata = {
                'job_id': job_id,
                'page_number': analysis.get('page_number'),
                'word_count': analysis.get('word_count', 0),
                'entities_found': len(analysis.get('entities', [])),
                'keywords': analysis.get('keywords', []),
                'language': analysis.get('language', {}).get('language', 'unknown'),
                'language_confidence': analysis.get('language', {}).get('confidence', 0),
                'processing_time': analysis.get('processing_time', 0),
                'text_length': len(clean_text)
            }
            
            # Gerar embedding
            embedding_result = embedding_engine.generate_embedding(
                text=clean_text,
                metadata=metadata
            )
            
            if not embedding_result or not embedding_result.vector:
                logger.warning(f"Falha na geração de embedding para página {metadata['page_number']}")
                return False
            
            # Adicionar ao banco vectorial
            doc_id = vector_db.add_document(
                text=clean_text,
                vector=embedding_result.vector,
                metadata=metadata,
                job_id=job_id,
                page_number=analysis.get('page_number'),
                lead_score=analysis.get('lead_score')
            )
            
            logger.debug(f"Documento adicionado ao banco vectorial: {doc_id}")
            
            # Salvar embedding individual
            await self._save_embedding_result(job_id, analysis.get('page_number'), embedding_result, doc_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar análise individual: {e}")
            return False
    
    def _load_text_analyses(self, job_id: str) -> List[Dict[str, Any]]:
        """Carrega análises de texto de um job"""
        try:
            # Buscar arquivos de análise
            analysis_dir = f"text_analysis/{job_id}"
            
            if not storage_manager.directory_exists(analysis_dir):
                return []
            
            files = storage_manager.list_files(analysis_dir)
            analyses = []
            
            for file_path in files:
                if file_path.endswith('_analysis.json'):
                    try:
                        analysis_data = storage_manager.load_json(file_path)
                        analyses.append(analysis_data)
                    except Exception as e:
                        logger.warning(f"Erro ao carregar análise {file_path}: {e}")
                        continue
            
            logger.debug(f"Carregadas {len(analyses)} análises de texto para job {job_id}")
            return analyses
            
        except Exception as e:
            logger.error(f"Erro ao carregar análises de texto para job {job_id}: {e}")
            return []
    
    async def _save_embedding_result(self, 
                                   job_id: str, 
                                   page_number: int, 
                                   embedding_result: EmbeddingResult,
                                   doc_id: str):
        """Salva resultado individual de embedding"""
        try:
            # Criar diretório de embeddings
            embeddings_dir = f"embeddings/{job_id}"
            storage_manager.ensure_directory(embeddings_dir)
            
            # Preparar dados para salvar
            embedding_data = {
                'document_id': doc_id,
                'job_id': job_id,
                'page_number': page_number,
                'text': embedding_result.text,
                'vector_dimension': embedding_result.vector_dimension,
                'model_name': embedding_result.model_name,
                'created_at': embedding_result.created_at,
                'metadata': embedding_result.metadata,
                # Não salvar o vetor completo aqui (já está no banco vectorial)
                'vector_preview': embedding_result.vector[:5] if len(embedding_result.vector) > 5 else embedding_result.vector
            }
            
            # Salvar arquivo de embedding
            embedding_file = f"{embeddings_dir}/page_{page_number}_embedding.json"
            storage_manager.save_json(embedding_file, embedding_data)
            
            logger.debug(f"Embedding salvo: {embedding_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar embedding: {e}")
    
    async def _save_embedding_stats(self, job_id: str, stats: Dict[str, Any]):
        """Salva estatísticas do processamento de embeddings"""
        try:
            embeddings_dir = f"embeddings/{job_id}"
            storage_manager.ensure_directory(embeddings_dir)
            
            stats_file = f"{embeddings_dir}/embedding_stats.json"
            storage_manager.save_json(stats_file, stats)
            
            logger.debug(f"Estatísticas de embedding salvas: {stats_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas: {e}")
    
    async def search_similar_documents(self, 
                                     query_text: str, 
                                     k: int = 10,
                                     threshold: float = 0.7,
                                     job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca documentos similares ao texto da query
        
        Args:
            query_text: Texto da busca
            k: Número máximo de resultados
            threshold: Threshold mínimo de similaridade
            job_id: Filtrar por job específico (opcional)
            
        Returns:
            Resultados da busca
        """
        try:
            # Gerar embedding da query
            query_embedding = embedding_engine.generate_embedding(query_text)
            
            if not query_embedding or not query_embedding.vector:
                return {
                    'query_text': query_text,
                    'status': 'error',
                    'error': 'Falha na geração de embedding da query',
                    'results': []
                }
            
            # Buscar no banco vectorial
            search_results = vector_db.search_similar(
                query_vector=query_embedding.vector,
                k=k,
                threshold=threshold
            )
            
            # Filtrar por job se especificado
            if job_id:
                search_results = [r for r in search_results if r.document.job_id == job_id]
            
            # Preparar resultados
            results = []
            for search_result in search_results:
                doc = search_result.document
                
                result_data = {
                    'document_id': doc.id,
                    'job_id': doc.job_id,
                    'page_number': doc.page_number,
                    'text_preview': doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                    'similarity': search_result.similarity,
                    'rank': search_result.rank,
                    'lead_score': doc.lead_score,
                    'metadata': doc.metadata
                }
                results.append(result_data)
            
            logger.info(f"Busca semântica concluída: {len(results)} resultados para '{query_text[:50]}...'")
            
            return {
                'query_text': query_text,
                'status': 'success',
                'total_results': len(results),
                'threshold_used': threshold,
                'model_used': embedding_engine.model_name,
                'query_vector_dimension': len(query_embedding.vector),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Erro na busca semântica: {e}")
            return {
                'query_text': query_text,
                'status': 'error',
                'error': str(e),
                'results': []
            }
    
    async def get_job_embeddings_info(self, job_id: str) -> Dict[str, Any]:
        """
        Obtém informações sobre embeddings de um job
        
        Args:
            job_id: ID do job
            
        Returns:
            Informações sobre embeddings do job
        """
        try:
            # Buscar documentos do job no banco vectorial
            job_documents = vector_db.search_by_job(job_id)
            
            if not job_documents:
                return {
                    'job_id': job_id,
                    'status': 'no_embeddings',
                    'message': 'Nenhum embedding encontrado para este job'
                }
            
            # Calcular estatísticas
            lead_scores = [doc.lead_score for doc in job_documents if doc.lead_score is not None]
            text_lengths = [len(doc.text) for doc in job_documents]
            
            info = {
                'job_id': job_id,
                'status': 'found',
                'embeddings_count': len(job_documents),
                'pages_with_embeddings': len(set(doc.page_number for doc in job_documents if doc.page_number)),
                'average_text_length': sum(text_lengths) / len(text_lengths) if text_lengths else 0,
                'documents_with_lead_scores': len(lead_scores),
                'average_lead_score': sum(lead_scores) / len(lead_scores) if lead_scores else 0,
                'max_lead_score': max(lead_scores) if lead_scores else 0,
                'vector_dimension': job_documents[0].vector[0] if job_documents else None,
                'model_used': embedding_engine.model_name,
                'created_range': {
                    'first': min(doc.created_at for doc in job_documents),
                    'last': max(doc.created_at for doc in job_documents)
                }
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações de embeddings: {e}")
            return {
                'job_id': job_id,
                'status': 'error',
                'error': str(e)
            }
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do worker"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'uptime_seconds': uptime,
            'processing_rate': self.processed_count / (uptime / 3600) if uptime > 0 else 0,  # por hora
            'error_rate': self.error_count / max(1, self.processed_count + self.error_count),
            'embedding_engine_info': embedding_engine.get_model_info(),
            'vector_db_stats': vector_db.get_stats()
        }

# Instância global do worker
embedding_worker = EmbeddingWorker() 