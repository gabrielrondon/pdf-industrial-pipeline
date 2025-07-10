import logging
import logging.config
import json
from datetime import datetime
from typing import Dict, Any, Optional
import sys
from pythonjsonlogger import jsonlogger
import contextvars
from functools import wraps
import time

from config.settings import get_settings

settings = get_settings()

# Context variables for request tracking
request_id_var = contextvars.ContextVar('request_id', default=None)
user_id_var = contextvars.ContextVar('user_id', default=None)


class ContextFilter(logging.Filter):
    """Add context variables to log records"""
    
    def filter(self, record):
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()
        record.environment = settings.environment
        record.app_name = settings.app_name
        record.app_version = settings.app_version
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add source location
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add context
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'environment'):
            log_record['environment'] = record.environment
        if hasattr(record, 'app_name'):
            log_record['app_name'] = record.app_name
        if hasattr(record, 'app_version'):
            log_record['app_version'] = record.app_version
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration"""
    
    # Different formats for different environments
    if settings.log_format == "json":
        formatter_class = "core.logging_config.CustomJsonFormatter"
        format_string = None
    else:
        formatter_class = "logging.Formatter"
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "context_filter": {
                "()": ContextFilter
            }
        },
        "formatters": {
            "default": {
                "class": formatter_class,
                "format": format_string
            } if format_string else {
                "()": formatter_class
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
                "filters": ["context_filter"]
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"logs/{settings.environment}.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "default",
                "filters": ["context_filter"]
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": settings.log_level
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO"
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": "WARNING" if not settings.debug else "INFO"
            }
        }
    }
    
    # Add error tracking handler in production
    if settings.environment == "production":
        config["handlers"]["sentry"] = {
            "class": "sentry_sdk.integrations.logging.EventHandler",
            "level": "ERROR"
        }
        config["loggers"][""]["handlers"].append("sentry")
    
    return config


def setup_logging():
    """Setup logging configuration"""
    import os
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Apply configuration
    logging.config.dictConfig(get_logging_config())
    
    # Set third-party loggers to WARNING to reduce noise
    for logger_name in ["urllib3", "boto3", "botocore", "aiobotocore"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


class LoggingMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)
        return self._logger


def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__module__)
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function executed successfully",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "args": str(args)[:100],  # Truncate for safety
                    "kwargs": str(kwargs)[:100]
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function execution failed",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "error": str(e),
                    "args": str(args)[:100],
                    "kwargs": str(kwargs)[:100]
                },
                exc_info=True
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__module__)
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function executed successfully",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function execution failed",
                extra={
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def log_database_query(query: str, params: Optional[Dict] = None, duration: Optional[float] = None):
    """Log database queries"""
    logger = logging.getLogger("database.queries")
    
    logger.debug(
        "Database query executed",
        extra={
            "query": query[:500],  # Truncate long queries
            "params": params,
            "duration": duration
        }
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: Optional[str] = None,
    request_size: Optional[int] = None,
    response_size: Optional[int] = None
):
    """Log API requests"""
    logger = logging.getLogger("api.requests")
    
    logger.info(
        f"{method} {path} - {status_code}",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "user_id": user_id,
            "request_size": request_size,
            "response_size": response_size
        }
    )


def log_job_event(
    job_id: str,
    event: str,
    status: str,
    details: Optional[Dict] = None
):
    """Log job processing events"""
    logger = logging.getLogger("jobs.events")
    
    logger.info(
        f"Job event: {event}",
        extra={
            "job_id": job_id,
            "event": event,
            "status": status,
            "details": details or {}
        }
    )


# Structured logging helpers
class StructuredLogger:
    """Helper class for structured logging"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
    
    def log_event(
        self,
        event_type: str,
        message: str,
        level: str = "INFO",
        **kwargs
    ):
        """Log a structured event"""
        log_method = getattr(self.logger, level.lower())
        log_method(
            message,
            extra={
                "event_type": event_type,
                **kwargs
            }
        )
    
    def log_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "count",
        tags: Optional[Dict] = None
    ):
        """Log a metric"""
        self.logger.info(
            f"Metric: {metric_name}",
            extra={
                "metric_name": metric_name,
                "metric_value": value,
                "metric_unit": unit,
                "metric_tags": tags or {}
            }
        )


# Performance logging
class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = StructuredLogger("performance")
    
    def log_operation(
        self,
        operation: str,
        duration: float,
        success: bool,
        **kwargs
    ):
        """Log operation performance"""
        self.logger.log_event(
            "operation_performance",
            f"{operation} completed",
            level="INFO" if success else "ERROR",
            operation=operation,
            duration=duration,
            success=success,
            **kwargs
        )
    
    def log_resource_usage(
        self,
        cpu_percent: float,
        memory_mb: float,
        disk_io_mb: Optional[float] = None,
        network_io_mb: Optional[float] = None
    ):
        """Log resource usage"""
        self.logger.log_event(
            "resource_usage",
            "Resource usage snapshot",
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            disk_io_mb=disk_io_mb,
            network_io_mb=network_io_mb
        )


# Initialize logging on module import
setup_logging()

# Create default loggers
api_logger = StructuredLogger("api")
job_logger = StructuredLogger("jobs")
ml_logger = StructuredLogger("ml")
perf_logger = PerformanceLogger()