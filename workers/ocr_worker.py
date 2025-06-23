"""
Worker de OCR - Etapa 2
Processa páginas que precisam de OCR usando o sistema de filas existente
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
from utils.image_utils import image_processor
from ocr.tesseract_engine import tesseract_engine

logger = logging.getLogger(__name__)

class OCRWorker:
    """Worker para processamento de OCR de páginas PDF"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.processing_stats = {
            'total_processed': 0,
            'successful_ocr': 0,
            'failed_ocr': 0,
            'start_time': None
        }
        
    def process_ocr_job(self, job_id: str, page_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa OCR para uma página específica
        
        Args:
            job_id: ID do job
            page_info: Informações da página (do manifest)
            
        Returns:
            Resultado do processamento OCR
        """
        try:
            logger.info(f"Iniciando OCR para job {job_id}, página {page_info.get('page_number', 'N/A')}")
            
            # Obter caminho do arquivo PDF da página
            page_file = page_info.get('file_path')
            if not page_file or not os.path.exists(page_file):
                raise FileNotFoundError(f"Arquivo da página não encontrado: {page_file}")
            
            # Converter PDF para imagem
            image_paths = self._pdf_to_images(page_file, job_id)
            if not image_paths:
                raise RuntimeError("Falha ao converter PDF para imagem")
            
            # Processar cada imagem (normalmente será apenas uma por página)
            ocr_results = []
            for image_path in image_paths:
                # Pré-processar imagem
                processed_image = self._preprocess_image(image_path, job_id)
                
                # Executar OCR
                ocr_result = self._extract_text(processed_image, page_info)
                ocr_results.append(ocr_result)
            
            # Consolidar resultados
            consolidated_result = self._consolidate_results(ocr_results, page_info)
            
            # Salvar resultados no storage
            storage_result = self._save_ocr_results(job_id, consolidated_result)
            
            # Atualizar estatísticas
            self.processing_stats['successful_ocr'] += 1
            self.processing_stats['total_processed'] += 1
            
            # Resultado final
            final_result = {
                'job_id': job_id,
                'page_number': page_info.get('page_number'),
                'ocr_status': 'success',
                'text_extracted': consolidated_result.get('text', ''),
                'confidence_avg': consolidated_result.get('confidence_stats', {}).get('avg_confidence', 0),
                'word_count': consolidated_result.get('word_count', 0),
                'char_count': consolidated_result.get('char_count', 0),
                'detected_language': consolidated_result.get('detected_language', 'unknown'),
                'storage_paths': storage_result,
                'processing_timestamp': datetime.now().isoformat(),
                'processing_time_seconds': consolidated_result.get('processing_time', 0)
            }
            
            logger.info(f"OCR concluído para job {job_id}, página {page_info.get('page_number')}: "
                       f"{final_result['char_count']} caracteres extraídos")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Erro no processamento OCR para job {job_id}: {e}")
            
            # Atualizar estatísticas de erro
            self.processing_stats['failed_ocr'] += 1
            self.processing_stats['total_processed'] += 1
            
            return {
                'job_id': job_id,
                'page_number': page_info.get('page_number'),
                'ocr_status': 'error',
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def _pdf_to_images(self, pdf_path: str, job_id: str) -> List[str]:
        """Converte página PDF para imagem"""
        try:
            # Criar diretório temporário para imagens
            temp_images_dir = os.path.join(self.temp_dir, f"ocr_images_{job_id}")
            os.makedirs(temp_images_dir, exist_ok=True)
            
            # Converter PDF para imagens
            image_paths = image_processor.pdf_to_images(
                pdf_path=pdf_path,
                output_dir=temp_images_dir,
                dpi=300,  # Alta resolução para melhor OCR
                format='PNG'
            )
            
            logger.debug(f"Convertidas {len(image_paths)} imagens para OCR")
            return image_paths
            
        except Exception as e:
            logger.error(f"Erro ao converter PDF para imagens: {e}")
            return []
    
    def _preprocess_image(self, image_path: str, job_id: str) -> str:
        """Pré-processa imagem para melhorar qualidade do OCR"""
        try:
            # Criar diretório para imagens processadas
            temp_processed_dir = os.path.join(self.temp_dir, f"ocr_processed_{job_id}")
            os.makedirs(temp_processed_dir, exist_ok=True)
            
            # Definir caminho de saída
            base_name = Path(image_path).stem
            output_path = os.path.join(temp_processed_dir, f"{base_name}_processed.png")
            
            # Pré-processar imagem
            processed_path = image_processor.preprocess_image(
                image_path=image_path,
                output_path=output_path,
                enhance_contrast=True,
                enhance_sharpness=True,
                remove_noise=True,
                binarize=False,  # Deixar colorido para melhor OCR
                auto_rotate=True
            )
            
            logger.debug(f"Imagem pré-processada: {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.warning(f"Erro no pré-processamento, usando imagem original: {e}")
            return image_path
    
    def _extract_text(self, image_path: str, page_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai texto da imagem usando Tesseract"""
        try:
            start_time = datetime.now()
            
            # Configurar OCR baseado no tipo de documento
            confidence_threshold = 30.0  # Threshold mínimo de confiança
            
            # Extrair texto
            ocr_result = tesseract_engine.extract_text(
                image_path=image_path,
                confidence_threshold=confidence_threshold
            )
            
            # Calcular tempo de processamento
            processing_time = (datetime.now() - start_time).total_seconds()
            ocr_result['processing_time'] = processing_time
            
            # Adicionar informações da página
            ocr_result['page_info'] = page_info
            ocr_result['image_path'] = image_path
            
            return ocr_result
            
        except Exception as e:
            logger.error(f"Erro na extração de texto: {e}")
            return {
                'text': '',
                'error': str(e),
                'image_path': image_path,
                'page_info': page_info,
                'processing_time': 0
            }
    
    def _consolidate_results(self, ocr_results: List[Dict[str, Any]], 
                           page_info: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida resultados de múltiplas imagens (se houver)"""
        if not ocr_results:
            return {
                'text': '',
                'word_count': 0,
                'char_count': 0,
                'confidence_stats': {'avg_confidence': 0},
                'detected_language': 'unknown',
                'processing_time': 0
            }
        
        # Se apenas um resultado, retornar diretamente
        if len(ocr_results) == 1:
            return ocr_results[0]
        
        # Consolidar múltiplos resultados
        consolidated_text = []
        total_words = 0
        total_chars = 0
        total_processing_time = 0
        confidences = []
        languages = []
        
        for result in ocr_results:
            if 'text' in result and result['text']:
                consolidated_text.append(result['text'])
                total_words += result.get('word_count', 0)
                total_chars += result.get('char_count', 0)
                total_processing_time += result.get('processing_time', 0)
                
                if 'confidence_stats' in result:
                    confidences.append(result['confidence_stats'].get('avg_confidence', 0))
                
                if 'detected_language' in result:
                    languages.append(result['detected_language'])
        
        # Calcular estatísticas consolidadas
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        most_common_language = max(set(languages), key=languages.count) if languages else 'unknown'
        
        return {
            'text': '\n'.join(consolidated_text),
            'word_count': total_words,
            'char_count': total_chars,
            'confidence_stats': {'avg_confidence': avg_confidence},
            'detected_language': most_common_language,
            'processing_time': total_processing_time,
            'page_info': page_info,
            'consolidated_from': len(ocr_results)
        }
    
    def _save_ocr_results(self, job_id: str, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Salva resultados do OCR no storage"""
        try:
            storage_paths = {}
            
            # Salvar texto extraído
            if ocr_result.get('text'):
                text_content = ocr_result['text']
                text_filename = f"page_{ocr_result.get('page_info', {}).get('page_number', 'unknown')}_ocr.txt"
                
                # Criar arquivo temporário com o texto
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                               suffix='.txt', delete=False) as temp_file:
                    temp_file.write(text_content)
                    temp_text_path = temp_file.name
                
                # Upload para storage
                text_result = storage_manager.upload_job_file(
                    job_id=job_id,
                    local_path=temp_text_path,
                    file_type='ocr'
                )
                storage_paths['text_file'] = text_result
                
                # Limpar arquivo temporário
                os.unlink(temp_text_path)
            
            # Salvar metadados do OCR
            metadata = {
                'ocr_result': ocr_result,
                'processing_timestamp': datetime.now().isoformat(),
                'tesseract_version': tesseract_engine._verify_tesseract if hasattr(tesseract_engine, '_verify_tesseract') else 'unknown'
            }
            
            metadata_filename = f"page_{ocr_result.get('page_info', {}).get('page_number', 'unknown')}_ocr_metadata.json"
            
            # Criar arquivo temporário com metadados
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                           suffix='.json', delete=False) as temp_file:
                json.dump(metadata, temp_file, indent=2, ensure_ascii=False)
                temp_metadata_path = temp_file.name
            
            # Upload para storage
            metadata_result = storage_manager.upload_job_file(
                job_id=job_id,
                local_path=temp_metadata_path,
                file_type='ocr'
            )
            storage_paths['metadata_file'] = metadata_result
            
            # Limpar arquivo temporário
            os.unlink(temp_metadata_path)
            
            logger.debug(f"Resultados OCR salvos no storage para job {job_id}")
            return storage_paths
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados OCR no storage: {e}")
            return {'error': str(e)}
    
    def process_queue_batch(self, max_items: int = 10) -> Dict[str, Any]:
        """
        Processa um lote de itens da fila de OCR
        
        Args:
            max_items: Número máximo de itens a processar
            
        Returns:
            Estatísticas do processamento
        """
        if not self.processing_stats['start_time']:
            self.processing_stats['start_time'] = datetime.now()
        
        processed_items = []
        
        try:
            # Verificar se há itens na fila
            if not queue_manager.is_available():
                logger.warning("Sistema de filas não está disponível")
                return {'error': 'Queue system not available'}
            
            # Processar itens da fila
            for _ in range(max_items):
                # Simular obtenção de item da fila (implementação específica depende do Redis)
                # Por enquanto, vamos usar uma implementação mock
                queue_item = self._get_next_ocr_item()
                
                if not queue_item:
                    break  # Não há mais itens na fila
                
                # Processar item
                result = self.process_ocr_job(
                    job_id=queue_item['job_id'],
                    page_info=queue_item['page_info']
                )
                
                processed_items.append(result)
                
                # Log do progresso
                logger.info(f"Processado item OCR {len(processed_items)}/{max_items}")
            
            # Estatísticas do lote
            batch_stats = {
                'items_processed': len(processed_items),
                'successful': len([item for item in processed_items if item.get('ocr_status') == 'success']),
                'failed': len([item for item in processed_items if item.get('ocr_status') == 'error']),
                'batch_timestamp': datetime.now().isoformat(),
                'processing_stats': self.processing_stats.copy(),
                'processed_items': processed_items
            }
            
            logger.info(f"Lote OCR processado: {batch_stats['successful']}/{batch_stats['items_processed']} sucessos")
            return batch_stats
            
        except Exception as e:
            logger.error(f"Erro no processamento do lote OCR: {e}")
            return {
                'error': str(e),
                'items_processed': len(processed_items),
                'processed_items': processed_items,
                'batch_timestamp': datetime.now().isoformat()
            }
    
    def _get_next_ocr_item(self) -> Optional[Dict[str, Any]]:
        """
        Obtém próximo item da fila de OCR
        
        Nota: Esta é uma implementação mock. A implementação real
        dependeria da estrutura específica do Redis/fila.
        """
        # TODO: Implementar integração real com Redis
        # Por enquanto, retorna None (fila vazia)
        return None
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de processamento"""
        stats = self.processing_stats.copy()
        
        if stats['start_time']:
            elapsed_time = (datetime.now() - stats['start_time']).total_seconds()
            stats['elapsed_time_seconds'] = elapsed_time
            
            if stats['total_processed'] > 0:
                stats['avg_processing_time'] = elapsed_time / stats['total_processed']
        
        return stats
    
    def cleanup_temp_files(self, job_id: str = None):
        """Limpa arquivos temporários"""
        try:
            if job_id:
                # Limpar arquivos específicos do job
                patterns = [f"ocr_images_{job_id}", f"ocr_processed_{job_id}"]
                for pattern in patterns:
                    temp_dir = os.path.join(self.temp_dir, pattern)
                    if os.path.exists(temp_dir):
                        import shutil
                        shutil.rmtree(temp_dir)
                        logger.debug(f"Diretório temporário removido: {temp_dir}")
            else:
                # Limpar todos os arquivos temporários de OCR
                import glob
                import shutil
                
                ocr_temp_dirs = glob.glob(os.path.join(self.temp_dir, "ocr_*"))
                for temp_dir in ocr_temp_dirs:
                    if os.path.isdir(temp_dir):
                        shutil.rmtree(temp_dir)
                        logger.debug(f"Diretório temporário removido: {temp_dir}")
                        
        except Exception as e:
            logger.warning(f"Erro ao limpar arquivos temporários: {e}")

# Instância global do worker
ocr_worker = OCRWorker() 