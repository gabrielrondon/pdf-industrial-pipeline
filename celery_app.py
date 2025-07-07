from celery import Celery
from celery.signals import setup_logging
from kombu import Queue, Exchange
import logging

from config.settings import get_settings

settings = get_settings()

# Create Celery app
app = Celery(
    'pdf_pipeline',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        'tasks.pdf_tasks',
        'tasks.ml_tasks',
        'tasks.analysis_tasks',
        'tasks.notification_tasks'
    ]
)

# Celery configuration
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'tasks.pdf_tasks.*': {'queue': 'pdf_processing'},
        'tasks.ml_tasks.*': {'queue': 'ml_processing'},
        'tasks.analysis_tasks.*': {'queue': 'analysis'},
        'tasks.notification_tasks.*': {'queue': 'notifications'},
    },
    
    # Worker settings
    worker_prefetch_multiplier=settings.celery_worker_prefetch_multiplier,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=True,
    
    # Task execution settings
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        'master_name': 'redis-master',
        'retry_on_timeout': True,
    },
    
    # Broker settings
    broker_transport_options={
        'visibility_timeout': 3600,  # 1 hour
        'fanout_prefix': True,
        'fanout_patterns': True,
    },
    
    # Queue definitions
    task_default_queue='default',
    task_queues=(
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('pdf_processing', Exchange('pdf'), routing_key='pdf.processing'),
        Queue('ml_processing', Exchange('ml'), routing_key='ml.processing'),
        Queue('analysis', Exchange('analysis'), routing_key='analysis.judicial'),
        Queue('notifications', Exchange('notifications'), routing_key='notifications.email'),
        Queue('priority', Exchange('priority'), routing_key='priority.high'),
    ),
    
    # Monitoring
    task_send_sent_event=True,
    task_track_started=True,
    worker_send_task_events=True,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        'cleanup-expired-jobs': {
            'task': 'tasks.maintenance_tasks.cleanup_expired_jobs',
            'schedule': 3600.0,  # Every hour
        },
        'health-check': {
            'task': 'tasks.maintenance_tasks.health_check',
            'schedule': 300.0,  # Every 5 minutes
        },
        'model-performance-check': {
            'task': 'tasks.ml_tasks.check_model_performance',
            'schedule': 86400.0,  # Daily
        },
    },
    
    # Error handling
    task_annotations={
        '*': {
            'rate_limit': '100/m',
            'time_limit': settings.celery_task_time_limit,
            'soft_time_limit': settings.celery_task_soft_time_limit,
        },
        'tasks.pdf_tasks.process_large_pdf': {
            'rate_limit': '10/m',
            'time_limit': 7200,  # 2 hours for large PDFs
        },
        'tasks.ml_tasks.train_model': {
            'rate_limit': '2/h',
            'time_limit': 14400,  # 4 hours for training
        },
    },
)

# Logging configuration
@setup_logging.connect
def config_loggers(*args, **kwargs):
    from core.logging_config import setup_logging
    setup_logging()


# Task failure callback
@app.task(bind=True)
def task_failure_handler(self, task_id, error, traceback):
    """Handle task failures"""
    logger = logging.getLogger('celery.task_failure')
    logger.error(
        f"Task {task_id} failed",
        extra={
            'task_id': task_id,
            'error': str(error),
            'traceback': traceback
        }
    )
    
    # Here you could implement notifications, retries, etc.
    # For example, send to dead letter queue or notify administrators


# Worker ready callback
@app.task(bind=True)
def worker_ready_handler(self):
    """Handle worker ready event"""
    logger = logging.getLogger('celery.worker')
    logger.info("Celery worker is ready")


if __name__ == '__main__':
    app.start()