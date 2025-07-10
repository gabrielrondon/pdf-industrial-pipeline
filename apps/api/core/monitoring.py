from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from prometheus_client.core import CollectorRegistry
from functools import wraps
import time
import psutil
from typing import Dict, Any, Optional, Callable
import asyncio
from datetime import datetime
import logging

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create a custom registry
registry = CollectorRegistry()

# Application Info
app_info = Info(
    'pdf_pipeline_app',
    'Application information',
    registry=registry
)
app_info.info({
    'version': settings.app_version,
    'environment': settings.environment
})

# Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    registry=registry
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

# Job Processing Metrics
jobs_total = Counter(
    'jobs_total',
    'Total number of jobs',
    ['status', 'job_type'],
    registry=registry
)

job_processing_duration_seconds = Histogram(
    'job_processing_duration_seconds',
    'Job processing duration',
    ['job_type', 'stage'],
    registry=registry
)

jobs_in_progress = Gauge(
    'jobs_in_progress',
    'Number of jobs currently being processed',
    ['job_type'],
    registry=registry
)

# PDF Processing Metrics
pdf_pages_processed_total = Counter(
    'pdf_pages_processed_total',
    'Total number of PDF pages processed',
    registry=registry
)

pdf_processing_errors_total = Counter(
    'pdf_processing_errors_total',
    'Total number of PDF processing errors',
    ['error_type'],
    registry=registry
)

pdf_file_size_bytes = Histogram(
    'pdf_file_size_bytes',
    'PDF file size distribution',
    registry=registry
)

# ML Model Metrics
ml_predictions_total = Counter(
    'ml_predictions_total',
    'Total number of ML predictions',
    ['model_name', 'model_version'],
    registry=registry
)

ml_inference_duration_seconds = Histogram(
    'ml_inference_duration_seconds',
    'ML model inference duration',
    ['model_name', 'model_version'],
    registry=registry
)

ml_model_accuracy = Gauge(
    'ml_model_accuracy',
    'ML model accuracy score',
    ['model_name', 'model_version'],
    registry=registry
)

# Database Metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    registry=registry
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type'],
    registry=registry
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total number of cache hits',
    ['cache_type'],
    registry=registry
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total number of cache misses',
    ['cache_type'],
    registry=registry
)

# System Metrics
system_cpu_usage_percent = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=registry
)

system_memory_usage_bytes = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    registry=registry
)

system_disk_usage_bytes = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes',
    ['mount_point'],
    registry=registry
)

# Queue Metrics
queue_size = Gauge(
    'queue_size',
    'Number of items in queue',
    ['queue_name'],
    registry=registry
)

queue_processing_time_seconds = Histogram(
    'queue_processing_time_seconds',
    'Queue item processing time',
    ['queue_name'],
    registry=registry
)

# Business Metrics
lead_scores_distribution = Histogram(
    'lead_scores_distribution',
    'Distribution of lead scores',
    registry=registry
)

judicial_analysis_duration_seconds = Histogram(
    'judicial_analysis_duration_seconds',
    'Judicial analysis processing time',
    registry=registry
)

high_value_leads_total = Counter(
    'high_value_leads_total',
    'Total number of high-value leads identified',
    registry=registry
)


class MetricsCollector:
    """Collect and update system metrics"""
    
    @staticmethod
    def collect_system_metrics():
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage_percent.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage_bytes.set(memory.used)
            
            # Disk usage
            for partition in psutil.disk_partitions():
                if partition.mountpoint:
                    usage = psutil.disk_usage(partition.mountpoint)
                    system_disk_usage_bytes.labels(
                        mount_point=partition.mountpoint
                    ).set(usage.used)
                    
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
    
    @staticmethod
    async def start_metrics_collection():
        """Start periodic metrics collection"""
        while True:
            MetricsCollector.collect_system_metrics()
            await asyncio.sleep(30)  # Collect every 30 seconds


def track_request_metrics(method: str, endpoint: str):
    """Decorator to track HTTP request metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 500  # Default to error
            
            try:
                # Track request
                result = await func(*args, **kwargs)
                status = getattr(result, 'status_code', 200)
                return result
                
            except Exception as e:
                status = getattr(e, 'status_code', 500)
                raise
                
            finally:
                # Record metrics
                duration = time.time() - start_time
                
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=str(status)
                ).inc()
                
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
                
        return wrapper
    return decorator


def track_job_metrics(job_type: str, stage: str):
    """Decorator to track job processing metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Increment jobs in progress
            jobs_in_progress.labels(job_type=job_type).inc()
            
            try:
                result = await func(*args, **kwargs)
                
                # Success metrics
                jobs_total.labels(status='success', job_type=job_type).inc()
                
                return result
                
            except Exception as e:
                # Error metrics
                jobs_total.labels(status='error', job_type=job_type).inc()
                pdf_processing_errors_total.labels(
                    error_type=type(e).__name__
                ).inc()
                raise
                
            finally:
                # Record duration
                duration = time.time() - start_time
                job_processing_duration_seconds.labels(
                    job_type=job_type,
                    stage=stage
                ).observe(duration)
                
                # Decrement jobs in progress
                jobs_in_progress.labels(job_type=job_type).dec()
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Increment jobs in progress
            jobs_in_progress.labels(job_type=job_type).inc()
            
            try:
                result = func(*args, **kwargs)
                
                # Success metrics
                jobs_total.labels(status='success', job_type=job_type).inc()
                
                return result
                
            except Exception as e:
                # Error metrics
                jobs_total.labels(status='error', job_type=job_type).inc()
                pdf_processing_errors_total.labels(
                    error_type=type(e).__name__
                ).inc()
                raise
                
            finally:
                # Record duration
                duration = time.time() - start_time
                job_processing_duration_seconds.labels(
                    job_type=job_type,
                    stage=stage
                ).observe(duration)
                
                # Decrement jobs in progress
                jobs_in_progress.labels(job_type=job_type).dec()
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def track_ml_inference(model_name: str, model_version: str):
    """Decorator to track ML inference metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record successful prediction
                ml_predictions_total.labels(
                    model_name=model_name,
                    model_version=model_version
                ).inc()
                
                return result
                
            finally:
                # Record inference time
                duration = time.time() - start_time
                ml_inference_duration_seconds.labels(
                    model_name=model_name,
                    model_version=model_version
                ).observe(duration)
                
        return wrapper
    return decorator


def track_database_query(query_type: str):
    """Decorator to track database query metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                return result
                
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    query_type=query_type
                ).observe(duration)
                
        return wrapper
    return decorator


def track_cache_access(cache_type: str):
    """Track cache hit/miss"""
    def hit():
        cache_hits_total.labels(cache_type=cache_type).inc()
    
    def miss():
        cache_misses_total.labels(cache_type=cache_type).inc()
    
    return hit, miss


class BusinessMetrics:
    """Track business-specific metrics"""
    
    @staticmethod
    def track_lead_score(score: float):
        """Track lead score distribution"""
        lead_scores_distribution.observe(score)
        
        # Track high-value leads
        if score > 0.8:
            high_value_leads_total.inc()
    
    @staticmethod
    def track_judicial_analysis(duration: float):
        """Track judicial analysis performance"""
        judicial_analysis_duration_seconds.observe(duration)
    
    @staticmethod
    def track_pdf_processing(page_count: int, file_size: int):
        """Track PDF processing metrics"""
        pdf_pages_processed_total.inc(page_count)
        pdf_file_size_bytes.observe(file_size)


class MetricsEndpoint:
    """Expose metrics endpoint for Prometheus"""
    
    @staticmethod
    def get_metrics() -> bytes:
        """Generate metrics in Prometheus format"""
        return generate_latest(registry)


# Health check metrics
class HealthCheck:
    """Application health check"""
    
    def __init__(self):
        self.checks = {}
    
    def add_check(self, name: str, check_func: Callable) -> None:
        """Add a health check"""
        self.checks[name] = check_func
    
    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                    
                results["checks"][name] = {
                    "status": "healthy" if result else "unhealthy",
                    "details": result
                }
                
                if not result:
                    results["status"] = "unhealthy"
                    
            except Exception as e:
                results["checks"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                results["status"] = "unhealthy"
        
        return results


# Create global health check instance
health_check = HealthCheck()


# OpenTelemetry integration placeholder
class TracingConfig:
    """OpenTelemetry tracing configuration"""
    
    @staticmethod
    def setup_tracing():
        """Setup distributed tracing"""
        if not settings.enable_tracing:
            return
            
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.jaeger import JaegerExporter
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            
            # Create tracer provider
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)
            
            # Create Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
            
            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            logger.info("Tracing enabled with Jaeger")
            
        except ImportError:
            logger.warning("OpenTelemetry not installed, tracing disabled")
        except Exception as e:
            logger.error(f"Failed to setup tracing: {str(e)}")