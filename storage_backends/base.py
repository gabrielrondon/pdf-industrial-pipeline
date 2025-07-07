from abc import ABC, abstractmethod
from typing import BinaryIO, List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import asyncio
from dataclasses import dataclass


@dataclass
class StorageObject:
    """Represents a stored object"""
    key: str
    size: int
    last_modified: datetime
    etag: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class StorageUploadResult:
    """Result of an upload operation"""
    key: str
    size: int
    etag: str
    version_id: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def upload(
        self,
        key: str,
        file_obj: BinaryIO,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> StorageUploadResult:
        """Upload a file to storage"""
        pass
    
    @abstractmethod
    async def upload_bytes(
        self,
        key: str,
        data: bytes,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> StorageUploadResult:
        """Upload bytes to storage"""
        pass
    
    @abstractmethod
    async def download(
        self,
        key: str,
        file_obj: BinaryIO
    ) -> int:
        """Download a file from storage to a file object"""
        pass
    
    @abstractmethod
    async def download_bytes(
        self,
        key: str
    ) -> bytes:
        """Download a file from storage as bytes"""
        pass
    
    @abstractmethod
    async def stream_download(
        self,
        key: str,
        chunk_size: int = 8192
    ) -> AsyncGenerator[bytes, None]:
        """Stream download a file in chunks"""
        pass
    
    @abstractmethod
    async def exists(
        self,
        key: str
    ) -> bool:
        """Check if a file exists"""
        pass
    
    @abstractmethod
    async def delete(
        self,
        key: str
    ) -> bool:
        """Delete a file"""
        pass
    
    @abstractmethod
    async def delete_many(
        self,
        keys: List[str]
    ) -> Dict[str, bool]:
        """Delete multiple files"""
        pass
    
    @abstractmethod
    async def list_objects(
        self,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
        continuation_token: Optional[str] = None
    ) -> tuple[List[StorageObject], Optional[str]]:
        """List objects with optional prefix"""
        pass
    
    @abstractmethod
    async def get_metadata(
        self,
        key: str
    ) -> Optional[StorageObject]:
        """Get object metadata"""
        pass
    
    @abstractmethod
    async def copy(
        self,
        source_key: str,
        dest_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Copy an object"""
        pass
    
    @abstractmethod
    async def move(
        self,
        source_key: str,
        dest_key: str
    ) -> bool:
        """Move an object"""
        pass
    
    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        method: str = "GET"
    ) -> str:
        """Generate a presigned URL for temporary access"""
        pass
    
    @abstractmethod
    async def get_storage_info(self) -> Dict[str, Any]:
        """Get storage backend information and stats"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if storage backend is healthy"""
        pass


class StorageError(Exception):
    """Base exception for storage operations"""
    pass


class StorageNotFoundError(StorageError):
    """Raised when object is not found"""
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"Object not found: {key}")


class StoragePermissionError(StorageError):
    """Raised when permission is denied"""
    pass


class StorageQuotaExceededError(StorageError):
    """Raised when storage quota is exceeded"""
    pass


class StorageConnectionError(StorageError):
    """Raised when connection to storage fails"""
    pass