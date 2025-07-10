import aioboto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import BinaryIO, List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import logging
from io import BytesIO

from .base import (
    StorageBackend, StorageObject, StorageUploadResult,
    StorageNotFoundError, StoragePermissionError,
    StorageConnectionError
)
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class S3Backend(StorageBackend):
    """AWS S3 / MinIO storage backend"""
    
    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        self.bucket = bucket
        self.region = region
        self.endpoint_url = endpoint_url
        
        # Create session with credentials if provided
        if access_key and secret_key:
            self.session = aioboto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        else:
            self.session = aioboto3.Session(region_name=region)
    
    def _get_client(self):
        """Get S3 client"""
        return self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            region_name=self.region
        )
    
    async def _ensure_bucket_exists(self):
        """Ensure bucket exists, create if not"""
        async with self._get_client() as client:
            try:
                await client.head_bucket(Bucket=self.bucket)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    # Create bucket
                    if self.region == 'us-east-1':
                        await client.create_bucket(Bucket=self.bucket)
                    else:
                        await client.create_bucket(
                            Bucket=self.bucket,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    logger.info(f"Created bucket: {self.bucket}")
                else:
                    raise StorageConnectionError(f"Failed to access bucket: {str(e)}")
    
    async def upload(
        self,
        key: str,
        file_obj: BinaryIO,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> StorageUploadResult:
        """Upload a file to S3"""
        try:
            await self._ensure_bucket_exists()
            
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Read file size
            file_obj.seek(0, 2)  # Seek to end
            size = file_obj.tell()
            file_obj.seek(0)  # Reset to beginning
            
            async with self._get_client() as client:
                response = await client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=file_obj.read(),
                    **extra_args
                )
            
            return StorageUploadResult(
                key=key,
                size=size,
                etag=response['ETag'].strip('"'),
                version_id=response.get('VersionId'),
                metadata=metadata
            )
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            if e.response['Error']['Code'] == 'AccessDenied':
                raise StoragePermissionError(f"Permission denied: {key}")
            raise StorageConnectionError(f"Upload failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected upload error: {str(e)}")
            raise StorageConnectionError(f"Upload failed: {str(e)}")
    
    async def upload_bytes(
        self,
        key: str,
        data: bytes,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> StorageUploadResult:
        """Upload bytes to S3"""
        file_obj = BytesIO(data)
        return await self.upload(key, file_obj, metadata, content_type)
    
    async def download(
        self,
        key: str,
        file_obj: BinaryIO
    ) -> int:
        """Download from S3 to file object"""
        try:
            async with self._get_client() as client:
                response = await client.get_object(Bucket=self.bucket, Key=key)
                data = await response['Body'].read()
                file_obj.write(data)
                return len(data)
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise StorageNotFoundError(key)
            raise StorageConnectionError(f"Download failed: {str(e)}")
    
    async def download_bytes(
        self,
        key: str
    ) -> bytes:
        """Download from S3 as bytes"""
        try:
            async with self._get_client() as client:
                response = await client.get_object(Bucket=self.bucket, Key=key)
                return await response['Body'].read()
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise StorageNotFoundError(key)
            raise StorageConnectionError(f"Download failed: {str(e)}")
    
    async def stream_download(
        self,
        key: str,
        chunk_size: int = 8192
    ) -> AsyncGenerator[bytes, None]:
        """Stream download from S3"""
        try:
            async with self._get_client() as client:
                response = await client.get_object(Bucket=self.bucket, Key=key)
                
                async for chunk in response['Body'].iter_chunks(chunk_size):
                    yield chunk
                    
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise StorageNotFoundError(key)
            raise StorageConnectionError(f"Stream download failed: {str(e)}")
    
    async def exists(
        self,
        key: str
    ) -> bool:
        """Check if object exists in S3"""
        try:
            async with self._get_client() as client:
                await client.head_object(Bucket=self.bucket, Key=key)
                return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise StorageConnectionError(f"Existence check failed: {str(e)}")
    
    async def delete(
        self,
        key: str
    ) -> bool:
        """Delete object from S3"""
        try:
            async with self._get_client() as client:
                await client.delete_object(Bucket=self.bucket, Key=key)
                return True
        except ClientError as e:
            logger.error(f"Delete error: {str(e)}")
            return False
    
    async def delete_many(
        self,
        keys: List[str]
    ) -> Dict[str, bool]:
        """Delete multiple objects from S3"""
        if not keys:
            return {}
        
        # S3 delete_objects has a limit of 1000 keys
        results = {}
        
        try:
            async with self._get_client() as client:
                for i in range(0, len(keys), 1000):
                    batch = keys[i:i+1000]
                    
                    response = await client.delete_objects(
                        Bucket=self.bucket,
                        Delete={
                            'Objects': [{'Key': key} for key in batch],
                            'Quiet': False
                        }
                    )
                    
                    # Process successful deletes
                    for deleted in response.get('Deleted', []):
                        results[deleted['Key']] = True
                    
                    # Process errors
                    for error in response.get('Errors', []):
                        results[error['Key']] = False
                        logger.error(f"Failed to delete {error['Key']}: {error['Message']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch delete error: {str(e)}")
            return {key: False for key in keys}
    
    async def list_objects(
        self,
        prefix: Optional[str] = None,
        max_keys: int = 1000,
        continuation_token: Optional[str] = None
    ) -> tuple[List[StorageObject], Optional[str]]:
        """List objects in S3"""
        try:
            params = {
                'Bucket': self.bucket,
                'MaxKeys': max_keys
            }
            
            if prefix:
                params['Prefix'] = prefix
            if continuation_token:
                params['ContinuationToken'] = continuation_token
            
            async with self._get_client() as client:
                response = await client.list_objects_v2(**params)
            
            objects = []
            for obj in response.get('Contents', []):
                objects.append(StorageObject(
                    key=obj['Key'],
                    size=obj['Size'],
                    last_modified=obj['LastModified'],
                    etag=obj['ETag'].strip('"')
                ))
            
            next_token = response.get('NextContinuationToken')
            return objects, next_token
            
        except ClientError as e:
            raise StorageConnectionError(f"List objects failed: {str(e)}")
    
    async def get_metadata(
        self,
        key: str
    ) -> Optional[StorageObject]:
        """Get object metadata from S3"""
        try:
            async with self._get_client() as client:
                response = await client.head_object(Bucket=self.bucket, Key=key)
            
            return StorageObject(
                key=key,
                size=response['ContentLength'],
                last_modified=response['LastModified'],
                etag=response['ETag'].strip('"'),
                metadata=response.get('Metadata', {})
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise StorageConnectionError(f"Get metadata failed: {str(e)}")
    
    async def copy(
        self,
        source_key: str,
        dest_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Copy object within S3"""
        try:
            copy_source = {'Bucket': self.bucket, 'Key': source_key}
            
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
                extra_args['MetadataDirective'] = 'REPLACE'
            
            async with self._get_client() as client:
                await client.copy_object(
                    Bucket=self.bucket,
                    CopySource=copy_source,
                    Key=dest_key,
                    **extra_args
                )
            
            return True
            
        except ClientError as e:
            logger.error(f"Copy error: {str(e)}")
            return False
    
    async def move(
        self,
        source_key: str,
        dest_key: str
    ) -> bool:
        """Move object within S3"""
        if await self.copy(source_key, dest_key):
            return await self.delete(source_key)
        return False
    
    async def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        method: str = "GET"
    ) -> str:
        """Generate presigned URL for S3 object"""
        try:
            async with self._get_client() as client:
                client_method = 'get_object' if method == 'GET' else 'put_object'
                
                url = await client.generate_presigned_url(
                    ClientMethod=client_method,
                    Params={'Bucket': self.bucket, 'Key': key},
                    ExpiresIn=expiration
                )
                
                return url
                
        except Exception as e:
            raise StorageConnectionError(f"Presigned URL generation failed: {str(e)}")
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """Get S3 storage information"""
        try:
            async with self._get_client() as client:
                # Get bucket location
                location_response = await client.get_bucket_location(Bucket=self.bucket)
                
                # Get bucket versioning
                versioning_response = await client.get_bucket_versioning(Bucket=self.bucket)
                
                # Get storage metrics
                # Note: This requires CloudWatch metrics to be enabled
                total_size = 0
                object_count = 0
                
                paginator = client.get_paginator('list_objects_v2')
                async for page in paginator.paginate(Bucket=self.bucket):
                    for obj in page.get('Contents', []):
                        total_size += obj['Size']
                        object_count += 1
                
                return {
                    'backend': 's3',
                    'bucket': self.bucket,
                    'region': location_response.get('LocationConstraint', 'us-east-1'),
                    'endpoint': self.endpoint_url,
                    'versioning': versioning_response.get('Status', 'Disabled'),
                    'object_count': object_count,
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2)
                }
                
        except Exception as e:
            logger.error(f"Failed to get storage info: {str(e)}")
            return {
                'backend': 's3',
                'bucket': self.bucket,
                'error': str(e)
            }
    
    async def health_check(self) -> bool:
        """Check S3 connection health"""
        try:
            async with self._get_client() as client:
                await client.head_bucket(Bucket=self.bucket)
            return True
        except Exception as e:
            logger.error(f"S3 health check failed: {str(e)}")
            return False