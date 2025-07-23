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
    
    # Worker settings - Otimizado para Railway 8GB/8vCPU
    worker_prefetch_multiplier=2,  # Aumentado para melhor throughput
    worker_max_tasks_per_child=500,  # Reduzido para evitar memory leaks
    worker_disable_rate_limits=True,
    worker_concurrency=6,  # Otimizado para Railway Hobby plan (8 vCPU)
    
    # Task execution settings - Timeouts dinâmicos
    task_time_limit=1800,  # 30min padrão (reduzido de 1h)
    task_soft_time_limit=1500,  # 25min soft limit
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Task timeouts específicos por tipo
    task_annotations={
        'tasks.pdf_tasks.process_pdf_upload': {'time_limit': 300, 'soft_time_limit': 240},  # 5min para upload
        'tasks.pdf_tasks.chunk_pdf': {'time_limit': 600, 'soft_time_limit': 480},  # 10min para chunking
        'tasks.analysis_tasks.start_analysis_pipeline': {'time_limit': 1200, 'soft_time_limit': 900},  # 20min para análise
        'tasks.ml_tasks.*': {'time_limit': 900, 'soft_time_limit': 720},  # 15min para ML
    },
    
    # Result backend settings - Otimizado
    result_expires=1800,  # 30min (reduzido para economizar memória)
    result_backend_transport_options={
        'master_name': 'redis-master',
        'retry_on_timeout': True,
        'max_connections': 20,  # Pool de conexões
    },
    
    # Broker settings - Performance melhorada
    broker_transport_options={
        'visibility_timeout': 1800,  # 30min (reduzido)
        'fanout_prefix': True,
        'fanout_patterns': True,
        'max_connections': 20,  # Pool de conexões
        'retry_on_timeout': True,
        'socket_keepalive': True,
        'socket_keepalive_options': {
            'TCP_KEEPIDLE': 1,
            'TCP_KEEPINTVL': 3,
            'TCP_KEEPCNT': 5,
        },
    },
    
    # Compressão para reduzir tráfego de rede
    task_compression='gzip',
    result_compression='gzip',
    
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
        # 🤖 NOVOS TASKS DE INTELIGÊNCIA AUTOMÁTICA
        'auto-retraining-check': {
            'task': 'tasks.ml_tasks.run_auto_retraining',
            'schedule': 86400.0,  # Daily - verifica se precisa retreinar
        },
        'identify-uncertain-predictions': {
            'task': 'tasks.ml_tasks.identify_uncertain_cases',
            'schedule': 21600.0,  # Every 6 hours - identifica casos incertos
        },
        'process-pending-feedback': {
            'task': 'tasks.ml_tasks.process_feedback_batch',
            'schedule': 43200.0,  # Every 12 hours - processa feedback acumulado
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