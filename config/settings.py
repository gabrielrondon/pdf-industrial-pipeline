from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List, Dict
import os
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="PDF Industrial Pipeline", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Security
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/pdf_pipeline",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # Storage
    storage_backend: str = Field(default="local", env="STORAGE_BACKEND")  # local, s3, minio
    storage_path: str = Field(default="./storage", env="STORAGE_PATH")
    s3_bucket: Optional[str] = Field(default=None, env="S3_BUCKET")
    s3_region: str = Field(default="us-east-1", env="S3_REGION")
    s3_endpoint_url: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # PDF Processing
    max_pdf_size_mb: int = Field(default=500, env="MAX_PDF_SIZE_MB")
    pdf_chunk_size: int = Field(default=5, env="PDF_CHUNK_SIZE")  # pages per chunk
    pdf_chunk_overlap: int = Field(default=1, env="PDF_CHUNK_OVERLAP")  # overlap pages
    ocr_languages: List[str] = Field(default=["por", "eng"], env="OCR_LANGUAGES")
    ocr_timeout: int = Field(default=300, env="OCR_TIMEOUT")  # 5 minutes
    
    # ML Configuration
    model_path: str = Field(default="./models", env="MODEL_PATH")
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        env="EMBEDDING_MODEL"
    )
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")
    faiss_index_type: str = Field(default="IVF1024,Flat", env="FAISS_INDEX_TYPE")
    ml_batch_size: int = Field(default=32, env="ML_BATCH_SIZE")
    ml_max_features: int = Field(default=100, env="ML_MAX_FEATURES")
    
    # Celery Configuration
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    celery_task_time_limit: int = Field(default=3600, env="CELERY_TASK_TIME_LIMIT")  # 1 hour
    celery_task_soft_time_limit: int = Field(default=3300, env="CELERY_TASK_SOFT_TIME_LIMIT")
    celery_worker_concurrency: int = Field(default=4, env="CELERY_WORKER_CONCURRENCY")
    celery_worker_prefetch_multiplier: int = Field(default=1, env="CELERY_WORKER_PREFETCH_MULTIPLIER")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    jaeger_host: str = Field(default="localhost", env="JAEGER_HOST")
    jaeger_port: int = Field(default=6831, env="JAEGER_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")  # seconds
    
    # Feature Flags
    enable_judicial_analysis: bool = Field(default=True, env="ENABLE_JUDICIAL_ANALYSIS")
    enable_ml_predictions: bool = Field(default=True, env="ENABLE_ML_PREDICTIONS")
    enable_semantic_search: bool = Field(default=True, env="ENABLE_SEMANTIC_SEARCH")
    enable_async_processing: bool = Field(default=True, env="ENABLE_ASYNC_PROCESSING")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ocr_languages", pre=True)
    def parse_ocr_languages(cls, v):
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v
    
    @property
    def database_url_async(self) -> str:
        """Convert sync database URL to async"""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    @property
    def max_pdf_size_bytes(self) -> int:
        """Get max PDF size in bytes"""
        return self.max_pdf_size_mb * 1024 * 1024
    
    def get_storage_config(self) -> Dict:
        """Get storage configuration based on backend"""
        if self.storage_backend == "s3":
            return {
                "bucket": self.s3_bucket,
                "region": self.s3_region,
                "endpoint_url": self.s3_endpoint_url,
                "access_key": self.aws_access_key_id,
                "secret_key": self.aws_secret_access_key
            }
        return {"path": self.storage_path}


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Environment-specific settings
class DevelopmentSettings(Settings):
    debug: bool = True
    log_level: str = "DEBUG"
    

class ProductionSettings(Settings):
    debug: bool = False
    log_level: str = "INFO"
    rate_limit_enabled: bool = True
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if v == "change-me-in-production":
            raise ValueError("Secret key must be changed in production")
        return v


class TestSettings(Settings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/pdf_pipeline_test"
    redis_url: str = "redis://localhost:6379/15"
    storage_path: str = "./test_storage"
    rate_limit_enabled: bool = False


def get_environment_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()