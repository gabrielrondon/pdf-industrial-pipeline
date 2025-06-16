"""
Metrics Collector - Stage 6 Performance

Coleta métricas para monitoramento:
- Métricas de API (latência, throughput)
- Métricas de recursos do sistema
- Métricas de negócio
"""

import time
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """Dados de uma métrica"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = None

class MetricsCollector:
    """Coletor de métricas simplificado"""
    
    def __init__(self):
        self.metrics = {}
        self.request_history = deque(maxlen=1000)
        self.counters = defaultdict(float)
        logger.info("MetricsCollector inicializado")
    
    def record_request(self, endpoint: str, duration_ms: float, status_code: int):
        """Registra uma requisição"""
        self.request_history.append({
            "timestamp": datetime.now(),
            "endpoint": endpoint,
            "duration_ms": duration_ms,
            "status_code": status_code
        })
        
        # Contadores
        self.counters["total_requests"] += 1
        if status_code >= 400:
            self.counters["error_requests"] += 1
        
        logger.debug(f"Request registrada: {endpoint} - {duration_ms:.2f}ms")
    
    def set_gauge(self, name: str, value: float):
        """Define valor de uma métrica"""
        self.metrics[name] = MetricData(
            name=name,
            value=value,
            timestamp=datetime.now()
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas"""
        recent_requests = list(self.request_history)[-100:]  # Últimas 100
        
        if not recent_requests:
            return {"total_requests": 0, "avg_duration_ms": 0}
        
        avg_duration = sum(r["duration_ms"] for r in recent_requests) / len(recent_requests)
        error_rate = len([r for r in recent_requests if r["status_code"] >= 400]) / len(recent_requests) * 100
        
        return {
            "total_requests": int(self.counters["total_requests"]),
            "error_requests": int(self.counters["error_requests"]),
            "avg_duration_ms": round(avg_duration, 2),
            "error_rate_percent": round(error_rate, 2),
            "metrics_count": len(self.metrics)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do coletor"""
        return {
            "status": "healthy",
            "metrics_count": len(self.metrics),
            "request_history_size": len(self.request_history)
        }

# Singleton
metrics_collector = MetricsCollector()

def monitor_performance(endpoint_name: str = None):
    """Decorador para monitorar performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                metrics_collector.record_request(endpoint, duration_ms, 200)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                metrics_collector.record_request(endpoint, duration_ms, 500)
                raise
        return wrapper
    return decorator 