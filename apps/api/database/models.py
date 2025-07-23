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


class DashboardCache(Base, TimestampMixin):
    """
    Cache table for dashboard statistics to improve performance.
    Statistics are pre-calculated and stored here instead of calculating on every request.
    """
    __tablename__ = "dashboard_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    cache_key = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "global_stats", "user_stats:{user_id}"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for global stats
    
    # Cached statistics (JSONB for flexible structure)
    statistics = Column(JSONB, nullable=False, default=dict)
    
    # Cache metadata
    expires_at = Column(DateTime(timezone=True), nullable=False)  # When cache expires
    calculation_time_ms = Column(Integer, default=0)  # How long it took to calculate
    record_count = Column(Integer, default=0)  # Number of records processed
    
    # Relationships
    user = relationship("User", backref="dashboard_caches")
    
    __table_args__ = (
        Index("idx_dashboard_cache_key_expires", "cache_key", "expires_at"),
        Index("idx_dashboard_cache_user_expires", "user_id", "expires_at"),
    )
    
    @classmethod
    def get_cache_key(cls, cache_type: str, user_id: str = None) -> str:
        """Generate consistent cache keys"""
        if user_id:
            return f"{cache_type}:user:{user_id}"
        return f"{cache_type}:global"
    
    def is_expired(self) -> bool:
        """Check if cache is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_fresh(self, max_age_minutes: int = 5) -> bool:
        """Check if cache is fresh (not expired and recently updated)"""
        if self.is_expired():
            return False
        age_minutes = (datetime.utcnow() - self.updated_at).total_seconds() / 60
        return age_minutes <= max_age_minutes


# Admin System Models

class AdminRole(Base, TimestampMixin):
    """Admin roles and permissions system"""
    __tablename__ = "admin_roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSONB, default=list)  # List of permission strings
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    admin_users = relationship("AdminUser", back_populates="role")
    
    __table_args__ = (
        Index("idx_admin_roles_name_active", "name", "is_active"),
    )


class AdminUser(Base, TimestampMixin):
    """Admin users with enhanced permissions"""  
    __tablename__ = "admin_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("admin_roles.id"), nullable=False)
    
    # Admin-specific fields
    admin_level = Column(Integer, default=1)  # 1=Admin, 2=Super Admin, 3=System Admin
    can_manage_admins = Column(Boolean, default=False)
    can_access_logs = Column(Boolean, default=True)
    can_manage_users = Column(Boolean, default=True)
    can_view_analytics = Column(Boolean, default=True)
    can_system_config = Column(Boolean, default=False)
    
    # Security
    last_login_at = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", backref="admin_profile")
    role = relationship("AdminRole", back_populates="admin_users")
    invited_by_user = relationship("User", foreign_keys=[user_id])
    admin_invitations = relationship("AdminInvitation", back_populates="invited_by")
    admin_sessions = relationship("AdminSession", back_populates="admin_user")
    
    __table_args__ = (
        Index("idx_admin_users_user_active", "user_id", "is_active"),
        Index("idx_admin_users_level", "admin_level"),
    )


class AdminInvitation(Base, TimestampMixin):
    """System for inviting new admins"""
    __tablename__ = "admin_invitations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("admin_roles.id"), nullable=False)
    
    # Status tracking
    status = Column(String(20), default="pending")  # pending, accepted, expired, cancelled
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Invitation details
    personal_message = Column(Text)
    permissions_preview = Column(JSONB, default=dict)
    
    # Relationships
    invited_by = relationship("AdminUser", back_populates="admin_invitations")
    role = relationship("AdminRole")
    
    __table_args__ = (
        Index("idx_admin_invitations_email_status", "email", "status"),
        Index("idx_admin_invitations_token", "token"),
        Index("idx_admin_invitations_expires", "expires_at"),
    )
    
    def is_expired(self) -> bool:
        """Check if invitation is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if invitation is valid and can be accepted"""
        return self.status == "pending" and not self.is_expired()


class AdminSession(Base, TimestampMixin):
    """Track admin sessions for security monitoring"""
    __tablename__ = "admin_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Session details
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)
    login_at = Column(DateTime(timezone=True), server_default=func.now())
    logout_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Security tracking
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="admin_sessions")
    
    __table_args__ = (
        Index("idx_admin_sessions_token_active", "session_token", "is_active"),
        Index("idx_admin_sessions_user_active", "admin_user_id", "is_active"),
        Index("idx_admin_sessions_expires", "expires_at"),
    )
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid"""
        return self.is_active and not self.is_expired()


class AdminAuditLog(Base, TimestampMixin):
    """Comprehensive audit log for admin actions"""
    __tablename__ = "admin_audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # create_user, delete_document, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # user, document, system, etc.
    resource_id = Column(String(255), index=True)  # ID of affected resource
    
    # Context
    details = Column(JSONB, default=dict)  # Additional context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Results
    success = Column(Boolean, nullable=False, index=True)
    error_message = Column(Text)
    
    # Relationships
    admin_user = relationship("AdminUser")
    
    __table_args__ = (
        Index("idx_admin_audit_action_date", "action", "created_at"),
        Index("idx_admin_audit_resource", "resource_type", "resource_id"),
        Index("idx_admin_audit_admin_date", "admin_user_id", "created_at"),
        Index("idx_admin_audit_success_date", "success", "created_at"),
    )


class SystemMonitoring(Base, TimestampMixin):
    """System monitoring and health metrics"""
    __tablename__ = "system_monitoring"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    
    # Metric details
    metric_type = Column(String(50), nullable=False, index=True)  # cpu_usage, memory_usage, etc.
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # percentage, bytes, count, etc.
    
    # Context
    source = Column(String(50), default="system")  # system, database, cache, etc.
    tags = Column(JSONB, default=dict)  # Additional metadata
    
    __table_args__ = (
        Index("idx_system_monitoring_type_date", "metric_type", "created_at"),
        Index("idx_system_monitoring_name_date", "metric_name", "created_at"),
        Index("idx_system_monitoring_source_date", "source", "created_at"),
    )


class UserActivityLog(Base, TimestampMixin):
    """Enhanced user activity tracking for admin monitoring"""
    __tablename__ = "user_activity_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Nullable for anonymous
    
    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # login, upload, download, etc.
    activity_details = Column(JSONB, default=dict)
    
    # Request context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    endpoint = Column(String(255))
    method = Column(String(10))
    
    # Performance metrics
    response_time_ms = Column(Integer)
    status_code = Column(Integer)
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index("idx_user_activity_type_date", "activity_type", "created_at"),
        Index("idx_user_activity_user_date", "user_id", "created_at"),
        Index("idx_user_activity_status_date", "status_code", "created_at"),
    )