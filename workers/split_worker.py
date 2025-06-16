import os
import subprocess
import json
import glob
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFSplitWorker:
    def __init__(self, temp_dir: str = "temp_splits"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
    
    def split_pdf(self, file_path: str, job_id: str) -> Dict:
        """
        Divide um PDF em páginas individuais usando qpdf
        
        Args:
            file_path: Caminho para o arquivo PDF
            job_id: ID único do job
            
        Returns:
            Dict com informações do processamento
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            # Criar diretório de saída para este job
            output_dir = os.path.join(self.temp_dir, job_id)
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"Iniciando divisão do PDF {file_path} para job {job_id}")
            
            # Dividir PDF usando qpdf
            split_pattern = os.path.join(output_dir, "page-%d.pdf")
            result = subprocess.run([
                "qpdf", 
                file_path, 
                "--split-pages", 
                "--", 
                split_pattern
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"Erro ao dividir PDF: {result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Contar páginas geradas
            page_files = sorted(glob.glob(os.path.join(output_dir, "page-*.pdf")))
            page_count = len(page_files)
            
            logger.info(f"PDF dividido com sucesso: {page_count} páginas geradas")
            
            # Gerar manifest
            manifest = self._generate_manifest(
                job_id=job_id,
                original_file=file_path,
                output_dir=output_dir,
                page_files=page_files,
                page_count=page_count
            )
            
            # Salvar manifest.json
            manifest_path = os.path.join(output_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Manifest gerado: {manifest_path}")
            
            return {
                "status": "success",
                "job_id": job_id,
                "page_count": page_count,
                "output_dir": output_dir,
                "manifest_path": manifest_path,
                "page_files": page_files
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento do job {job_id}: {str(e)}")
            return {
                "status": "error",
                "job_id": job_id,
                "error": str(e)
            }
    
    def _generate_manifest(self, job_id: str, original_file: str, output_dir: str, 
                          page_files: List[str], page_count: int) -> Dict:
        """
        Gera manifest com metadados do processamento
        """
        # Obter informações do arquivo original
        original_stats = os.stat(original_file)
        original_size = original_stats.st_size
        
        # Gerar informações das páginas
        pages_info = []
        for i, page_file in enumerate(page_files, 1):
            page_stats = os.stat(page_file)
            pages_info.append({
                "page_number": i,
                "filename": os.path.basename(page_file),
                "file_path": page_file,
                "file_size": page_stats.st_size,
                "created_at": datetime.fromtimestamp(page_stats.st_ctime).isoformat()
            })
        
        manifest = {
            "job_id": job_id,
            "processing_info": {
                "processed_at": datetime.now().isoformat(),
                "processor": "qpdf",
                "status": "completed"
            },
            "original_file": {
                "filename": os.path.basename(original_file),
                "file_path": original_file,
                "file_size": original_size,
                "created_at": datetime.fromtimestamp(original_stats.st_ctime).isoformat()
            },
            "output_info": {
                "output_directory": output_dir,
                "total_pages": page_count,
                "pages": pages_info
            },
            "next_steps": {
                "ocr_required": self._check_ocr_required(original_file),
                "ready_for_processing": True
            }
        }
        
        return manifest
    
    def _check_ocr_required(self, file_path: str) -> bool:
        """
        Verifica rapidamente se o PDF precisa de OCR
        Implementação básica - pode ser melhorada
        """
        try:
            from pdfminer.high_level import extract_text
            
            # Extrair texto das primeiras páginas para verificar
            text = extract_text(file_path, maxpages=3)
            
            # Se extrair pouco texto, provavelmente precisa de OCR
            clean_text = text.strip()
            if len(clean_text) < 100:  # Limiar configurável
                return True
            
            # Verificar se há muito texto repetido ou caracteres estranhos
            words = clean_text.split()
            if len(words) < 20:
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Erro ao verificar necessidade de OCR: {e}")
            # Em caso de erro, assumir que precisa de OCR
            return True
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Recupera o status de um job através do manifest
        """
        manifest_path = os.path.join(self.temp_dir, job_id, "manifest.json")
        
        if not os.path.exists(manifest_path):
            return None
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler manifest do job {job_id}: {e}")
            return None
    
    def cleanup_job(self, job_id: str) -> bool:
        """
        Remove arquivos temporários de um job
        """
        import shutil
        
        job_dir = os.path.join(self.temp_dir, job_id)
        
        if os.path.exists(job_dir):
            try:
                shutil.rmtree(job_dir)
                logger.info(f"Arquivos do job {job_id} removidos")
                return True
            except Exception as e:
                logger.error(f"Erro ao remover arquivos do job {job_id}: {e}")
                return False
        
        return False

# Instância global do worker
pdf_split_worker = PDFSplitWorker()

def split_pdf_task(file_path: str, job_id: str) -> Dict:
    """
    Função auxiliar para divisão de PDF
    """
    return pdf_split_worker.split_pdf(file_path, job_id)
