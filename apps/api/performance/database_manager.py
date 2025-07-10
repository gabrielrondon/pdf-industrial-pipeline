"""
Database Manager - Stage 6 Performance

Gerencia base de dados PostgreSQL para metadados e analytics:
- Armazenamento de metadados de jobs
- Histórico de performance
- Cache de configurações
- Analytics e métricas
- Auditoria e logs
"""

import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Configuração do banco de dados"""
    host: str = "postgres"
    port: int = 5432
    database: str = "pdf_pipeline"
    username: str = "pipeline_user"
    password: str = "pipeline_pass"
    min_connections: int = 5
    max_connections: int = 20

@dataclass
class JobMetadata:
    """Metadados de um job"""
    job_id: str
    filename: str
    file_size: int
    page_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    lead_score: Optional[float] = None
    pipeline_stage: Optional[str] = None

class DatabaseManager:
    """
    Gerenciador de banco PostgreSQL
    Implementação simplificada para Stage 6
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.is_connected = False
        self.jobs_cache = {}  # Simulação até PostgreSQL estar disponível
        self.metrics_cache = []
        
        logger.info("DatabaseManager inicializado (modo simulação)")
    
    def save_job_metadata(self, metadata: JobMetadata) -> bool:
        """Salva metadados de um job"""
        try:
            self.jobs_cache[metadata.job_id] = metadata
            logger.debug(f"Job metadata salvo: {metadata.job_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar job metadata: {e}")
            return False
    
    def get_job_metadata(self, job_id: str) -> Optional[JobMetadata]:
        """Recupera metadados de um job"""
        return self.jobs_cache.get(job_id)
    
    def update_job_status(self, job_id: str, status: str, error_message: str = None) -> bool:
        """Atualiza status de um job"""
        try:
            if job_id in self.jobs_cache:
                metadata = self.jobs_cache[job_id]
                metadata.status = status
                metadata.updated_at = datetime.now()
                metadata.error_message = error_message
                logger.debug(f"Job status atualizado: {job_id} -> {status}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar job status: {e}")
            return False
    
    def get_pipeline_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Recupera analytics do pipeline"""
        try:
            since = datetime.now() - timedelta(days=days)
            
            # Filtrar jobs recentes
            recent_jobs = [
                job for job in self.jobs_cache.values()
                if job.created_at >= since
            ]
            
            if not recent_jobs:
                return {"period_days": days, "job_statistics": {}}
            
            completed_jobs = [j for j in recent_jobs if j.status == 'completed']
            failed_jobs = [j for j in recent_jobs if j.status == 'failed']
            
            processing_times = [j.processing_time_ms for j in recent_jobs if j.processing_time_ms]
            lead_scores = [j.lead_score for j in recent_jobs if j.lead_score]
            
            return {
                "period_days": days,
                "job_statistics": {
                    "total_jobs": len(recent_jobs),
                    "completed_jobs": len(completed_jobs),
                    "failed_jobs": len(failed_jobs),
                    "avg_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
                    "total_pages": sum(j.page_count for j in recent_jobs),
                    "avg_lead_score": sum(lead_scores) / len(lead_scores) if lead_scores else 0
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar analytics: {e}")
            return {}
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do banco de dados"""
        return {
            "status": "healthy_simulation",
            "jobs_count": len(self.jobs_cache),
            "metrics_count": len(self.metrics_cache),
            "note": "Usando cache em memória até PostgreSQL estar disponível"
        }

# Singleton instance
database_manager = DatabaseManager() 