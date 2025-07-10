"""
Text Processing Worker - Etapa 3
Worker para processamento de texto após OCR
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import tempfile

# Importar componentes existentes
from .queue_manager import queue_manager
from utils.storage_manager import storage_manager
from text_processing.text_engine import text_engine, asdict

logger = logging.getLogger(__name__)

class TextWorker:
    """Worker para processamento de texto e extração de leads"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.processing_stats = {
            'total_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'leads_detected': 0,
            'start_time': None
        }
        
    def process_text_job(self, job_id: str, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Processa texto de resultado OCR para extrair informações de negócio"""
        try:
            logger.info(f"Iniciando processamento de texto para job {job_id}")
            
            # Obter texto extraído do OCR
            extracted_text = ocr_result.get('text_extracted', '')
            page_number = ocr_result.get('page_number', 1)
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                logger.warning(f"Texto insuficiente para processamento: job {job_id}")
                return self._create_empty_result(job_id, page_number, "Texto insuficiente")
            
            # Processar texto com o engine
            text_result = text_engine.process_text(extracted_text, job_id, page_number)
            
            # Salvar resultados no storage
            storage_result = self._save_text_results(job_id, text_result)
            
            # Criar resultado consolidado
            final_result = {
                'job_id': job_id,
                'page_number': page_number,
                'text_processing_status': 'success',
                'text_analysis': asdict(text_result),
                'storage_paths': storage_result,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Verificar se é um lead potencial
            lead_score = text_result.lead_indicators.get('lead_score', 0.0)
            if lead_score > 50.0:
                self.processing_stats['leads_detected'] += 1
                final_result['is_potential_lead'] = True
                logger.info(f"🎯 Lead potencial detectado! Score: {lead_score}")
            else:
                final_result['is_potential_lead'] = False
            
            self.processing_stats['successful_processing'] += 1
            self.processing_stats['total_processed'] += 1
            
            return final_result
            
        except Exception as e:
            logger.error(f"Erro no processamento de texto: {e}")
            self.processing_stats['failed_processing'] += 1
            self.processing_stats['total_processed'] += 1
            
            return {
                'job_id': job_id,
                'page_number': ocr_result.get('page_number', 1),
                'text_processing_status': 'error',
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def _create_empty_result(self, job_id: str, page_number: int, reason: str) -> Dict[str, Any]:
        """Cria resultado vazio quando não há texto suficiente"""
        return {
            'job_id': job_id,
            'page_number': page_number,
            'text_processing_status': 'skipped',
            'reason': reason,
            'processing_timestamp': datetime.now().isoformat(),
            'is_potential_lead': False
        }
    
    def _save_text_results(self, job_id: str, text_result) -> Dict[str, Any]:
        """Salva resultados do processamento de texto no storage"""
        try:
            # Criar diretório para resultados de texto
            text_dir = f"text_analysis/{job_id}"
            storage_manager.ensure_directory(text_dir)
            
            # Arquivo principal com análise completa
            analysis_file = f"{text_dir}/page_{text_result.page_number}_analysis.json"
            analysis_data = asdict(text_result)
            
            # Salvar análise completa
            storage_manager.save_json(analysis_file, analysis_data)
            
            # Arquivo de texto limpo para indexação futura
            clean_text_file = f"{text_dir}/page_{text_result.page_number}_clean_text.txt"
            storage_manager.save_text(clean_text_file, text_result.cleaned_text)
            
            return {
                'analysis_file': analysis_file,
                'clean_text_file': clean_text_file,
                'files_saved': 2,
                'storage_backend': storage_manager.get_storage_info()['backend']
            }
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados de texto: {e}")
            return {
                'error': str(e),
                'files_saved': 0
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de processamento"""
        stats = self.processing_stats.copy()
        if stats['total_processed'] > 0:
            stats['success_rate'] = stats['successful_processing'] / stats['total_processed']
            stats['lead_detection_rate'] = stats['leads_detected'] / stats['total_processed']
        else:
            stats['success_rate'] = 0.0
            stats['lead_detection_rate'] = 0.0
        
        return stats

# Instância global do worker
text_worker = TextWorker() 