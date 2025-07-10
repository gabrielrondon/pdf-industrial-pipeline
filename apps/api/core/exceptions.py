from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for API errors"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.extra_data = extra_data or {}


# Authentication Exceptions
class AuthenticationError(BaseAPIException):
    """Raised when authentication fails"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_001",
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    
    def __init__(self):
        super().__init__(detail="Invalid username or password")
        self.error_code = "AUTH_002"


class TokenExpiredError(AuthenticationError):
    """Raised when token has expired"""
    
    def __init__(self):
        super().__init__(detail="Token has expired")
        self.error_code = "AUTH_003"


class InsufficientPermissionsError(BaseAPIException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, required_permission: Optional[str] = None):
        detail = "Insufficient permissions"
        if required_permission:
            detail = f"Missing required permission: {required_permission}"
        
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTH_004"
        )


# Resource Exceptions
class ResourceNotFoundError(BaseAPIException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} with id '{resource_id}' not found",
            error_code="RESOURCE_001",
            extra_data={"resource_type": resource_type, "resource_id": resource_id}
        )


class ResourceAlreadyExistsError(BaseAPIException):
    """Raised when trying to create a resource that already exists"""
    
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource_type} with identifier '{identifier}' already exists",
            error_code="RESOURCE_002",
            extra_data={"resource_type": resource_type, "identifier": identifier}
        )


# Validation Exceptions
class ValidationError(BaseAPIException):
    """Raised when validation fails"""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_001",
            extra_data={"field": field} if field else {}
        )


class FileSizeExceededError(ValidationError):
    """Raised when file size exceeds limit"""
    
    def __init__(self, max_size_mb: int):
        super().__init__(
            detail=f"File size exceeds maximum allowed size of {max_size_mb}MB",
            field="file"
        )
        self.error_code = "VALIDATION_002"


class InvalidFileFormatError(ValidationError):
    """Raised when file format is invalid"""
    
    def __init__(self, expected_format: str, received_format: str):
        super().__init__(
            detail=f"Invalid file format. Expected {expected_format}, received {received_format}",
            field="file"
        )
        self.error_code = "VALIDATION_003"
        self.extra_data.update({
            "expected_format": expected_format,
            "received_format": received_format
        })


# Processing Exceptions
class ProcessingError(BaseAPIException):
    """Base class for processing errors"""
    
    def __init__(self, detail: str, job_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="PROCESSING_001",
            extra_data={"job_id": job_id} if job_id else {}
        )


class PDFProcessingError(ProcessingError):
    """Raised when PDF processing fails"""
    
    def __init__(self, detail: str, job_id: Optional[str] = None, page: Optional[int] = None):
        super().__init__(detail=f"PDF processing failed: {detail}", job_id=job_id)
        self.error_code = "PROCESSING_002"
        if page:
            self.extra_data["page"] = page


class OCRError(ProcessingError):
    """Raised when OCR processing fails"""
    
    def __init__(self, detail: str, job_id: Optional[str] = None):
        super().__init__(detail=f"OCR processing failed: {detail}", job_id=job_id)
        self.error_code = "PROCESSING_003"


class MLModelError(ProcessingError):
    """Raised when ML model operations fail"""
    
    def __init__(self, detail: str, model_name: Optional[str] = None):
        super().__init__(detail=f"ML model error: {detail}")
        self.error_code = "PROCESSING_004"
        if model_name:
            self.extra_data["model_name"] = model_name


# Storage Exceptions
class StorageError(BaseAPIException):
    """Base class for storage errors"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="STORAGE_001"
        )


class FileNotFoundError(StorageError):
    """Raised when file is not found in storage"""
    
    def __init__(self, file_path: str):
        super().__init__(detail=f"File not found: {file_path}")
        self.error_code = "STORAGE_002"
        self.extra_data = {"file_path": file_path}


class StorageQuotaExceededError(StorageError):
    """Raised when storage quota is exceeded"""
    
    def __init__(self, quota_mb: int, used_mb: int):
        super().__init__(
            detail=f"Storage quota exceeded. Quota: {quota_mb}MB, Used: {used_mb}MB"
        )
        self.error_code = "STORAGE_003"
        self.extra_data = {"quota_mb": quota_mb, "used_mb": used_mb}


# Rate Limiting Exceptions
class RateLimitExceededError(BaseAPIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            error_code="RATE_001",
            headers={"Retry-After": str(retry_after)},
            extra_data={"retry_after": retry_after}
        )


# Database Exceptions
class DatabaseError(BaseAPIException):
    """Base class for database errors"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}",
            error_code="DB_001"
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""
    
    def __init__(self):
        super().__init__(detail="Failed to connect to database")
        self.error_code = "DB_002"


class TransactionError(DatabaseError):
    """Raised when database transaction fails"""
    
    def __init__(self, operation: str):
        super().__init__(detail=f"Transaction failed during {operation}")
        self.error_code = "DB_003"
        self.extra_data = {"operation": operation}


# External Service Exceptions
class ExternalServiceError(BaseAPIException):
    """Base class for external service errors"""
    
    def __init__(self, service_name: str, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} service error: {detail}",
            error_code="EXTERNAL_001",
            extra_data={"service_name": service_name}
        )


class RedisConnectionError(ExternalServiceError):
    """Raised when Redis connection fails"""
    
    def __init__(self):
        super().__init__("Redis", "Failed to connect to Redis")
        self.error_code = "EXTERNAL_002"


class S3Error(ExternalServiceError):
    """Raised when S3 operations fail"""
    
    def __init__(self, operation: str, detail: str):
        super().__init__("S3", f"{operation} failed: {detail}")
        self.error_code = "EXTERNAL_003"
        self.extra_data["operation"] = operation


# Business Logic Exceptions
class BusinessLogicError(BaseAPIException):
    """Base class for business logic errors"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BUSINESS_001"
        )


class JobAlreadyProcessedError(BusinessLogicError):
    """Raised when trying to process an already processed job"""
    
    def __init__(self, job_id: str):
        super().__init__(detail=f"Job {job_id} has already been processed")
        self.error_code = "BUSINESS_002"
        self.extra_data = {"job_id": job_id}


class InvalidJobStateError(BusinessLogicError):
    """Raised when job is in invalid state for operation"""
    
    def __init__(self, job_id: str, current_state: str, required_state: str):
        super().__init__(
            detail=f"Job {job_id} is in state '{current_state}', but '{required_state}' is required"
        )
        self.error_code = "BUSINESS_003"
        self.extra_data = {
            "job_id": job_id,
            "current_state": current_state,
            "required_state": required_state
        }