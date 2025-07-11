from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    CHUNKED = "chunked"
    ANALYZED = "analyzed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobResponse(BaseModel):
    """Job information response"""
    id: str
    filename: str
    file_size: int
    status: JobStatus
    priority: int
    page_count: Optional[int] = None
    created_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class JobCreateResponse(BaseModel):
    """Job creation response"""
    job_id: str
    status: str
    message: str
    task_id: Optional[str] = None


class JobListResponse(BaseModel):
    """Job list response"""
    jobs: List[JobResponse]
    total: int
    skip: int
    limit: int


class JobStatusResponse(BaseModel):
    """Detailed job status response"""
    job_id: str
    status: JobStatus
    progress: Optional[int] = None
    total_steps: int = 4
    current_step: str = ""
    created_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    task_status: Optional[str] = None
    task_info: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None


# Authentication Schemas
class UserLogin(BaseModel):
    """User login request"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserCreate(BaseModel):
    """User creation request"""
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=255)
    
    @validator('email')
    def validate_email(cls, v):
        import re
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User information response"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    scopes: List[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = Field(None, gt=0, le=365)


class APIKeyResponse(BaseModel):
    """API key response"""
    id: str
    name: str
    key: str
    scopes: List[str]
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analysis Schemas
class JudicialAnalysisResponse(BaseModel):
    """Judicial analysis result"""
    job_id: str
    auction_type: Optional[str] = None
    case_number: Optional[str] = None
    court: Optional[str] = None
    property_type: Optional[str] = None
    property_address: Optional[str] = None
    evaluation_value: Optional[float] = None
    minimum_bid_value: Optional[float] = None
    debt_amount: Optional[float] = None
    risk_score: Optional[float] = None
    risk_factors: Dict[str, Any] = Field(default_factory=dict)
    compliance_status: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        from_attributes = True


class MLPredictionResponse(BaseModel):
    """ML prediction result"""
    job_id: str
    model_name: str
    model_version: str
    lead_score: Optional[float] = None
    confidence: Optional[float] = None
    predictions: Dict[str, Any] = Field(default_factory=dict)
    feature_importance: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        from_attributes = True


# Search Schemas
class SemanticSearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """Search result item"""
    job_id: str
    chunk_id: str
    score: float
    text_snippet: str
    page_range: str
    job_metadata: Dict[str, Any] = Field(default_factory=dict)


class SemanticSearchResponse(BaseModel):
    """Semantic search response"""
    query: str
    results: List[SearchResult]
    total_found: int
    search_time_ms: float


class LeadSearchRequest(BaseModel):
    """Lead search request"""
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)
    max_results: int = Field(default=50, ge=1, le=200)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None


class LeadSearchResult(BaseModel):
    """Lead search result"""
    job_id: str
    filename: str
    lead_score: float
    confidence: float
    created_at: datetime
    judicial_analysis: Optional[Dict[str, Any]] = None
    key_insights: List[str] = Field(default_factory=list)


class LeadSearchResponse(BaseModel):
    """Lead search response"""
    results: List[LeadSearchResult]
    total_found: int
    filters_applied: Dict[str, Any]
    search_time_ms: float


# Admin Schemas
class SystemStatsResponse(BaseModel):
    """System statistics"""
    total_jobs: int
    jobs_by_status: Dict[str, int]
    total_users: int
    active_users: int
    storage_usage_mb: float
    average_processing_time: float
    success_rate: float
    last_updated: datetime


class SystemHealthResponse(BaseModel):
    """System health status"""
    status: str
    timestamp: datetime
    checks: Dict[str, Dict[str, Any]]
    uptime_seconds: float


# Error Schemas
class ErrorResponse(BaseModel):
    """Error response"""
    error: Dict[str, Any] = Field(..., example={
        "code": "VALIDATION_001",
        "message": "Validation failed",
        "details": {}
    })


# Pagination
class PaginatedResponse(BaseModel):
    """Base paginated response"""
    total: int
    skip: int
    limit: int
    has_next: bool
    has_previous: bool
    
    @validator('has_next', always=True)
    def set_has_next(cls, v, values):
        return values.get('skip', 0) + values.get('limit', 0) < values.get('total', 0)
    
    @validator('has_previous', always=True)
    def set_has_previous(cls, v, values):
        return values.get('skip', 0) > 0


# Configuration Schemas
class JobConfigRequest(BaseModel):
    """Job configuration request"""
    chunk_size: int = Field(default=5, ge=1, le=20)
    chunk_overlap: int = Field(default=1, ge=0, le=5)
    enable_ocr: bool = True
    ocr_languages: List[str] = Field(default=["por", "eng"])
    enable_ml_analysis: bool = True
    enable_judicial_analysis: bool = True
    priority: int = Field(default=0, ge=0, le=10)


# Webhook Schemas
class WebhookRequest(BaseModel):
    """Webhook configuration request"""
    url: str = Field(..., regex=r'^https?://.+')
    events: List[str] = Field(..., min_items=1)
    secret: Optional[str] = None
    enabled: bool = True


class WebhookResponse(BaseModel):
    """Webhook configuration response"""
    id: str
    url: str
    events: List[str]
    enabled: bool
    created_at: datetime
    last_triggered: Optional[datetime] = None
    
    class Config:
        from_attributes = True