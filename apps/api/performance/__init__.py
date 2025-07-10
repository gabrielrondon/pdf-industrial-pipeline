"""
Performance & Scaling Module

Stage 6: Scaling & Performance
- Cache inteligente com Redis
- Processamento paralelo
- Otimização de banco de dados
- Monitoramento e métricas
- Load balancing
"""

from .cache_manager import cache_manager
from .parallel_processor import parallel_processor
from .database_manager import database_manager
from .metrics_collector import metrics_collector
from .monitoring import health_monitor
from .performance_utils import performance_utils

__all__ = [
    'cache_manager',
    'parallel_processor', 
    'database_manager',
    'metrics_collector',
    'health_monitor',
    'performance_utils'
] 