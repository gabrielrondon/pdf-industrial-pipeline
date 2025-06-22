import redis
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueueMessage:
    """Estrutura de mensagem para filas"""
    job_id: str
    message_type: str  # 'ocr', 'split', 'analysis', etc.
    payload: Dict
    created_at: str
    priority: int = 1  # 1=alta, 2=média, 3=baixa
    retry_count: int = 0
    max_retries: int = 3

class QueueManager:
    """Gerenciador de filas usando Redis"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Testar conexão
            self.redis_client.ping()
            logger.info(f"Conectado ao Redis: {redis_host}:{redis_port}")
        except redis.ConnectionError:
            logger.warning("Redis não disponível - usando modo simulado")
            self.redis_client = None
        
        # Nomes das filas
        self.QUEUE_OCR = "queue:ocr"
        self.QUEUE_ANALYSIS = "queue:analysis"
        self.QUEUE_FAILED = "queue:failed"
        self.QUEUE_COMPLETED = "queue:completed"
    
    def is_available(self) -> bool:
        """Verifica se Redis está disponível"""
        return self.redis_client is not None
    
    def enqueue_ocr_job(self, job_id: str, page_files: List[str], original_file: str) -> bool:
        """
        Enfileira job de OCR para páginas que precisam
        """
        try:
            for i, page_file in enumerate(page_files, 1):
                message = QueueMessage(
                    job_id=job_id,
                    message_type="ocr",
                    payload={
                        "page_number": i,
                        "page_file": page_file,
                        "original_file": original_file,
                        "output_dir": os.path.dirname(page_file)
                    },
                    created_at=datetime.now().isoformat(),
                    priority=1  # OCR é alta prioridade
                )
                
                if self.redis_client:
                    self.redis_client.lpush(self.QUEUE_OCR, json.dumps(asdict(message)))
                    logger.info(f"Job OCR enfileirado: {job_id} - página {i}")
                else:
                    logger.info(f"SIMULADO - Job OCR enfileirado: {job_id} - página {i}")
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao enfileirar job OCR {job_id}: {e}")
            return False
    
    def enqueue_analysis_job(self, job_id: str, manifest_path: str) -> bool:
        """
        Enfileira job de análise após OCR completar
        """
        try:
            message = QueueMessage(
                job_id=job_id,
                message_type="analysis",
                payload={
                    "manifest_path": manifest_path,
                    "analysis_type": "lead_detection"
                },
                created_at=datetime.now().isoformat(),
                priority=2  # Análise é média prioridade
            )
            
            if self.redis_client:
                self.redis_client.lpush(self.QUEUE_ANALYSIS, json.dumps(asdict(message)))
                logger.info(f"Job análise enfileirado: {job_id}")
            else:
                logger.info(f"SIMULADO - Job análise enfileirado: {job_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao enfileirar job análise {job_id}: {e}")
            return False
    
    def dequeue_message(self, queue_name: str, timeout: int = 10) -> Optional[QueueMessage]:
        """
        Remove mensagem da fila (blocking pop)
        """
        try:
            if not self.redis_client:
                return None
            
            result = self.redis_client.brpop(queue_name, timeout=timeout)
            if result:
                _, message_json = result
                message_data = json.loads(message_json)
                return QueueMessage(**message_data)
            
            return None
        
        except Exception as e:
            logger.error(f"Erro ao remover mensagem da fila {queue_name}: {e}")
            return None
    
    def get_queue_status(self) -> Dict[str, int]:
        """
        Retorna status de todas as filas
        """
        try:
            if not self.redis_client:
                return {
                    "ocr": 0,
                    "analysis": 0,
                    "failed": 0,
                    "completed": 0,
                    "redis_available": False
                }
            
            return {
                "ocr": self.redis_client.llen(self.QUEUE_OCR),
                "analysis": self.redis_client.llen(self.QUEUE_ANALYSIS),
                "failed": self.redis_client.llen(self.QUEUE_FAILED),
                "completed": self.redis_client.llen(self.QUEUE_COMPLETED),
                "redis_available": True
            }
        
        except Exception as e:
            logger.error(f"Erro ao obter status das filas: {e}")
            return {"error": str(e), "redis_available": False}
    
    def mark_job_completed(self, job_id: str, result: Dict) -> bool:
        """
        Marca job como concluído
        """
        try:
            message = QueueMessage(
                job_id=job_id,
                message_type="completed",
                payload=result,
                created_at=datetime.now().isoformat()
            )
            
            if self.redis_client:
                self.redis_client.lpush(self.QUEUE_COMPLETED, json.dumps(asdict(message)))
                logger.info(f"Job marcado como concluído: {job_id}")
            else:
                logger.info(f"SIMULADO - Job marcado como concluído: {job_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao marcar job como concluído {job_id}: {e}")
            return False
    
    def mark_job_failed(self, job_id: str, error: str, retry: bool = True) -> bool:
        """
        Marca job como falhado e opcionalmente re-enfileira
        """
        try:
            message = QueueMessage(
                job_id=job_id,
                message_type="failed",
                payload={"error": error, "retry": retry},
                created_at=datetime.now().isoformat()
            )
            
            if self.redis_client:
                self.redis_client.lpush(self.QUEUE_FAILED, json.dumps(asdict(message)))
                logger.error(f"Job marcado como falhado: {job_id} - {error}")
            else:
                logger.error(f"SIMULADO - Job marcado como falhado: {job_id} - {error}")
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao marcar job como falhado {job_id}: {e}")
            return False
    
    def job_exists(self, job_id: str) -> bool:
        """
        Verifica se um job existe (checando se há arquivos no storage)
        """
        try:
            from utils.storage_manager import storage_manager
            
            # Verificar se existe manifest do job
            manifest_path = f"jobs/{job_id}/metadata/manifest.json"
            return storage_manager.file_exists(manifest_path)
        
        except Exception as e:
            logger.error(f"Erro ao verificar existência do job {job_id}: {e}")
            return False
    
    def clear_all_queues(self) -> bool:
        """
        Limpa todas as filas (usado para testes)
        """
        try:
            if not self.redis_client:
                logger.info("SIMULADO - Todas as filas limpas")
                return True
            
            queues = [self.QUEUE_OCR, self.QUEUE_ANALYSIS, self.QUEUE_FAILED, self.QUEUE_COMPLETED]
            for queue in queues:
                self.redis_client.delete(queue)
            
            logger.info("Todas as filas limpas")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao limpar filas: {e}")
            return False

# Instância global do gerenciador
queue_manager = QueueManager()

def enqueue_ocr_pages(job_id: str, pages_needing_ocr: List[str], original_file: str) -> bool:
    """
    Função auxiliar para enfileirar páginas que precisam de OCR
    """
    if not pages_needing_ocr:
        logger.info(f"Job {job_id}: Nenhuma página precisa de OCR")
        return True
    
    return queue_manager.enqueue_ocr_job(job_id, pages_needing_ocr, original_file)

def get_queues_status() -> Dict[str, int]:
    """
    Função auxiliar para obter status das filas
    """
    return queue_manager.get_queue_status() 