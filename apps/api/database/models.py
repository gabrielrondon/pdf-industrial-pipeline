from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_users_email_active", "email", "is_active"),
    )


class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    scopes = Column(ARRAY(String), default=list)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"
    __table_args__ = (
        Index("idx_jobs_user_status", "user_id", "status"),
        Index("idx_jobs_created_at", "created_at"),
        Index("idx_jobs_status_created", "status", "created_at"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)
    priority = Column(Integer, default=0, nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    title = Column(String(500), nullable=True)  # User-editable title
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64))
    mime_type = Column(String(100))
    page_count = Column(Integer)
    
    # Processing metadata
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    processing_time_seconds = Column(Float)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Configuration
    config = Column(JSONB, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    chunks = relationship("JobChunk", back_populates="job", cascade="all, delete-orphan")
    text_analyses = relationship("TextAnalysis", back_populates="job", cascade="all, delete-orphan")
    ml_predictions = relationship("MLPrediction", back_populates="job", cascade="all, delete-orphan")
    judicial_analyses = relationship("JudicialAnalysis", back_populates="job", cascade="all, delete-orphan")


class JobChunk(Base, TimestampMixin):
    __tablename__ = "job_chunks"
    __table_args__ = (
        Index("idx_chunks_job_number", "job_id", "chunk_number"),
        Index("idx_chunks_search_vector", "search_vector", postgresql_using="gin"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    chunk_number = Column(Integer, nullable=False)
    page_start = Column(Integer, nullable=False)
    page_end = Column(Integer, nullable=False)
    
    # Content
    raw_text = Column(Text)
    cleaned_text = Column(Text)
    ocr_confidence = Column(Float)
    language = Column(String(10))
    
    # Search
    search_vector = Column(TSVECTOR)
    
    # Processing status
    status = Column(String(50), default="pending")
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    job = relationship("Job", back_populates="chunks")
    embeddings = relationship("Embedding", back_populates="chunk", cascade="all, delete-orphan")


class TextAnalysis(Base, TimestampMixin):
    __tablename__ = "text_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("job_chunks.id"))
    
    # NLP Results
    entities = Column(JSONB, default=dict)  # {persons: [], organizations: [], locations: [], etc}
    keywords = Column(ARRAY(String), default=list)
    topics = Column(JSONB, default=dict)  # {topic: confidence}
    sentiment = Column(JSONB, default=dict)  # {polarity: 0.0, subjectivity: 0.0}
    
    # Domain-specific
    business_indicators = Column(JSONB, default=dict)
    financial_data = Column(JSONB, default=dict)
    legal_references = Column(ARRAY(String), default=list)
    
    # Relationships
    job = relationship("Job", back_populates="text_analyses")


class Embedding(Base):
    __tablename__ = "embeddings"
    __table_args__ = (
        Index("idx_embeddings_chunk", "chunk_id"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("job_chunks.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    
    # Vector storage (using pgvector extension)
    # vector = Column(Vector(dimension))  # Uncomment when pgvector is available
    vector_json = Column(JSONB)  # Temporary storage as JSON
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chunk = relationship("JobChunk", back_populates="embeddings")


class MLPrediction(Base, TimestampMixin):
    __tablename__ = "ml_predictions"
    __table_args__ = (
        Index("idx_predictions_job_model", "job_id", "model_name"),
        Index("idx_predictions_score", "lead_score"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    # Model information
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    
    # Predictions
    lead_score = Column(Float, index=True)
    confidence = Column(Float)
    predictions = Column(JSONB, default=dict)
    feature_importance = Column(JSONB, default=dict)
    
    # Metadata
    inference_time_ms = Column(Float)
    
    # Relationships
    job = relationship("Job", back_populates="ml_predictions")


class JudicialAnalysis(Base, TimestampMixin):
    __tablename__ = "judicial_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    # Analysis results
    auction_type = Column(String(50))  # judicial, extrajudicial
    case_number = Column(String(100), index=True)
    court = Column(String(200))
    judge = Column(String(200))
    
    # Property information
    property_type = Column(String(100))
    property_address = Column(Text)
    property_registration = Column(String(100))
    property_area_m2 = Column(Float)
    
    # Financial information
    evaluation_value = Column(Float)
    minimum_bid_value = Column(Float)
    debt_amount = Column(Float)
    
    # Dates
    auction_date = Column(DateTime(timezone=True))
    publication_date = Column(DateTime(timezone=True))
    
    # Risk assessment
    risk_score = Column(Float)
    risk_factors = Column(JSONB, default=dict)
    compliance_status = Column(JSONB, default=dict)
    
    # Additional data
    parties_involved = Column(JSONB, default=dict)
    legal_restrictions = Column(ARRAY(String), default=list)
    occupation_status = Column(String(100))
    
    # Full analysis
    full_analysis = Column(JSONB, default=dict)
    
    # Relationships
    job = relationship("Job", back_populates="judicial_analyses")


class ProcessingMetrics(Base):
    __tablename__ = "processing_metrics"
    __table_args__ = (
        Index("idx_metrics_timestamp", "timestamp"),
        Index("idx_metrics_job", "job_id"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Performance metrics
    stage = Column(String(50), nullable=False)
    duration_seconds = Column(Float, nullable=False)
    cpu_usage_percent = Column(Float)
    memory_usage_mb = Column(Float)
    
    # Counters
    pages_processed = Column(Integer)
    chunks_created = Column(Integer)
    errors_count = Column(Integer)
    
    # Additional metrics
    metrics = Column(JSONB, default=dict)


# Association table for many-to-many relationships
job_tags = Table(
    "job_tags",
    Base.metadata,
    Column("job_id", UUID(as_uuid=True), ForeignKey("jobs.id"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)
)


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color
    
    # Many-to-many relationship
    jobs = relationship("Job", secondary=job_tags, backref="tags")