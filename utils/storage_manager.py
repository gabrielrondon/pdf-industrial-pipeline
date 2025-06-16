import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

logger = logging.getLogger(__name__)

class StorageBackend(ABC):
    """Interface abstrata para diferentes backends de armazenamento"""
    
    @abstractmethod
    def upload_file(self, local_path: str, storage_path: str) -> Dict[str, Any]:
        """Upload de arquivo para o storage"""
        pass
    
    @abstractmethod
    def download_file(self, storage_path: str, local_path: str) -> bool:
        """Download de arquivo do storage"""
        pass
    
    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """Deletar arquivo do storage"""
        pass
    
    @abstractmethod
    def file_exists(self, storage_path: str) -> bool:
        """Verificar se arquivo existe"""
        pass
    
    @abstractmethod
    def list_files(self, prefix: str) -> List[str]:
        """Listar arquivos com prefixo"""
        pass
    
    @abstractmethod
    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> Optional[str]:
        """Obter URL de acesso ao arquivo"""
        pass

class LocalStorage(StorageBackend):
    """Backend de armazenamento local"""
    
    def __init__(self, base_path: str = "storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        logger.info(f"LocalStorage inicializado em: {self.base_path.absolute()}")
    
    def upload_file(self, local_path: str, storage_path: str) -> Dict[str, Any]:
        """Upload de arquivo para storage local"""
        try:
            source = Path(local_path)
            destination = self.base_path / storage_path
            
            # Criar diretórios se necessário
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar arquivo
            import shutil
            shutil.copy2(source, destination)
            
            return {
                "success": True,
                "storage_path": storage_path,
                "local_path": str(destination),
                "size": destination.stat().st_size,
                "uploaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro no upload local: {e}")
            return {"success": False, "error": str(e)}
    
    def download_file(self, storage_path: str, local_path: str) -> bool:
        """Download de arquivo do storage local"""
        try:
            source = self.base_path / storage_path
            destination = Path(local_path)
            
            if not source.exists():
                return False
            
            destination.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            logger.error(f"Erro no download local: {e}")
            return False
    
    def delete_file(self, storage_path: str) -> bool:
        """Deletar arquivo do storage local"""
        try:
            file_path = self.base_path / storage_path
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo local: {e}")
            return False
    
    def file_exists(self, storage_path: str) -> bool:
        """Verificar se arquivo existe no storage local"""
        return (self.base_path / storage_path).exists()
    
    def list_files(self, prefix: str) -> List[str]:
        """Listar arquivos com prefixo no storage local"""
        try:
            prefix_path = self.base_path / prefix
            if not prefix_path.exists():
                return []
            
            files = []
            for file_path in prefix_path.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.base_path)
                    files.append(str(relative_path))
            return files
        except Exception as e:
            logger.error(f"Erro ao listar arquivos locais: {e}")
            return []
    
    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> Optional[str]:
        """Obter URL de acesso ao arquivo local"""
        file_path = self.base_path / storage_path
        if file_path.exists():
            return f"file://{file_path.absolute()}"
        return None

class StorageManager:
    """Gerenciador principal de armazenamento"""
    
    def __init__(self):
        self.backend = self._initialize_backend()
    
    def _initialize_backend(self) -> StorageBackend:
        """Inicializar backend baseado na configuração"""
        storage_type = os.getenv('STORAGE_TYPE', 'local').lower()
        
        if storage_type == 'local':
            base_path = os.getenv('LOCAL_STORAGE_PATH', 'storage')
            return LocalStorage(base_path)
        else:
            logger.warning(f"Tipo de storage desconhecido: {storage_type}, usando local")
            return LocalStorage()
    
    def upload_job_file(self, job_id: str, local_path: str, 
                       file_type: str = "original") -> Dict[str, Any]:
        """Upload de arquivo relacionado a um job"""
        filename = Path(local_path).name
        storage_path = f"jobs/{job_id}/{file_type}/{filename}"
        
        result = self.backend.upload_file(local_path, storage_path)
        if result.get("success"):
            result["job_id"] = job_id
            result["file_type"] = file_type
        
        return result
    
    def download_job_file(self, job_id: str, filename: str, 
                         file_type: str = "original", 
                         local_path: Optional[str] = None) -> Optional[str]:
        """Download de arquivo de um job"""
        storage_path = f"jobs/{job_id}/{file_type}/{filename}"
        
        if not local_path:
            local_path = f"temp_downloads/{job_id}_{filename}"
        
        if self.backend.download_file(storage_path, local_path):
            return local_path
        return None
    
    def delete_job(self, job_id: str) -> bool:
        """Deletar todos os arquivos de um job"""
        try:
            files = self.backend.list_files(f"jobs/{job_id}")
            success_count = 0
            
            for file_path in files:
                if self.backend.delete_file(file_path):
                    success_count += 1
            
            logger.info(f"Job {job_id}: {success_count}/{len(files)} arquivos deletados")
            return success_count == len(files)
        except Exception as e:
            logger.error(f"Erro ao deletar job {job_id}: {e}")
            return False
    
    def get_job_file_url(self, job_id: str, filename: str, 
                        file_type: str = "original", 
                        expires_in: int = 3600) -> Optional[str]:
        """Obter URL de acesso a arquivo de job"""
        storage_path = f"jobs/{job_id}/{file_type}/{filename}"
        return self.backend.get_file_url(storage_path, expires_in)
    
    def list_job_files(self, job_id: str, file_type: Optional[str] = None) -> List[str]:
        """Listar arquivos de um job"""
        if file_type:
            prefix = f"jobs/{job_id}/{file_type}"
        else:
            prefix = f"jobs/{job_id}"
        
        return self.backend.list_files(prefix)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Obter informações sobre o storage atual"""
        backend_type = type(self.backend).__name__
        info = {
            "backend": backend_type,
            "available": True
        }
        
        if isinstance(self.backend, LocalStorage):
            info["base_path"] = str(self.backend.base_path.absolute())
        
        return info

# Instância global do storage manager
storage_manager = StorageManager()
