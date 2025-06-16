"""
Performance Utilities - Stage 6 Performance

Utilitários para otimização de performance:
- Profiling e benchmarking
- Otimizações de memória
- Compression e serialização
- Rate limiting
- Connection pooling
"""

import time
import gzip
import pickle
import json
import logging
from typing import Any, Dict, Callable, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class PerformanceProfile:
    """Perfil de performance de uma função"""
    function_name: str
    call_count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    memory_usage_mb: float

@dataclass
class BenchmarkResult:
    """Resultado de benchmark"""
    function_name: str
    iterations: int
    total_time: float
    avg_time_per_iteration: float
    operations_per_second: float
    memory_peak_mb: float

class PerformanceProfiler:
    """Profiler simples para monitorar performance"""
    
    def __init__(self):
        self.profiles = defaultdict(list)
        self.start_times = {}
        logger.info("PerformanceProfiler inicializado")
    
    def start_timing(self, function_name: str):
        """Inicia medição de tempo"""
        self.start_times[function_name] = time.time()
    
    def end_timing(self, function_name: str):
        """Finaliza medição e registra"""
        if function_name in self.start_times:
            elapsed = time.time() - self.start_times[function_name]
            self.profiles[function_name].append(elapsed)
            del self.start_times[function_name]
            return elapsed
        return 0.0
    
    def get_profile(self, function_name: str) -> Optional[PerformanceProfile]:
        """Retorna perfil de uma função"""
        times = self.profiles.get(function_name, [])
        if not times:
            return None
        
        return PerformanceProfile(
            function_name=function_name,
            call_count=len(times),
            total_time=sum(times),
            avg_time=sum(times) / len(times),
            min_time=min(times),
            max_time=max(times),
            memory_usage_mb=0.0  # Implementação simplificada
        )
    
    def get_all_profiles(self) -> List[PerformanceProfile]:
        """Retorna todos os perfis"""
        profiles = []
        for function_name in self.profiles:
            profile = self.get_profile(function_name)
            if profile:
                profiles.append(profile)
        return profiles

class RateLimiter:
    """Rate limiter simples"""
    
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = deque()
    
    def is_allowed(self) -> bool:
        """Verifica se chamada é permitida"""
        now = time.time()
        
        # Remove chamadas antigas
        while self.calls and self.calls[0] < now - self.window_seconds:
            self.calls.popleft()
        
        # Verifica limite
        if len(self.calls) >= self.max_calls:
            return False
        
        # Registra chamada
        self.calls.append(now)
        return True
    
    def wait_time(self) -> float:
        """Retorna tempo de espera necessário"""
        if not self.calls:
            return 0.0
        
        oldest_call = self.calls[0]
        wait_time = (oldest_call + self.window_seconds) - time.time()
        return max(0.0, wait_time)

class CompressionUtils:
    """Utilitários de compressão"""
    
    @staticmethod
    def compress_data(data: Any, use_pickle: bool = True) -> bytes:
        """Comprime dados"""
        if use_pickle:
            serialized = pickle.dumps(data)
        else:
            serialized = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        return gzip.compress(serialized)
    
    @staticmethod
    def decompress_data(compressed_data: bytes, use_pickle: bool = True) -> Any:
        """Descomprime dados"""
        decompressed = gzip.decompress(compressed_data)
        
        if use_pickle:
            return pickle.loads(decompressed)
        else:
            return json.loads(decompressed.decode('utf-8'))
    
    @staticmethod
    def get_compression_ratio(original_data: Any) -> Dict[str, Any]:
        """Calcula taxa de compressão"""
        # Testar JSON
        json_data = json.dumps(original_data, ensure_ascii=False).encode('utf-8')
        json_compressed = gzip.compress(json_data)
        
        # Testar Pickle
        pickle_data = pickle.dumps(original_data)
        pickle_compressed = gzip.compress(pickle_data)
        
        return {
            "original_size_bytes": len(json_data),
            "json_compressed_size": len(json_compressed),
            "pickle_compressed_size": len(pickle_compressed),
            "json_compression_ratio": len(json_data) / len(json_compressed),
            "pickle_compression_ratio": len(pickle_data) / len(pickle_compressed),
            "best_method": "pickle" if len(pickle_compressed) < len(json_compressed) else "json"
        }

class CacheOptimizer:
    """Otimizador de cache"""
    
    def __init__(self):
        self.access_counts = defaultdict(int)
        self.access_times = defaultdict(list)
    
    def record_access(self, key: str):
        """Registra acesso a uma chave"""
        self.access_counts[key] += 1
        self.access_times[key].append(time.time())
        
        # Manter apenas últimos 100 acessos
        if len(self.access_times[key]) > 100:
            self.access_times[key] = self.access_times[key][-100:]
    
    def get_hot_keys(self, top_n: int = 10) -> List[str]:
        """Retorna chaves mais acessadas"""
        sorted_keys = sorted(self.access_counts.items(), key=lambda x: x[1], reverse=True)
        return [key for key, count in sorted_keys[:top_n]]
    
    def should_cache(self, key: str, threshold_accesses: int = 3) -> bool:
        """Determina se uma chave deve ser cacheada"""
        return self.access_counts.get(key, 0) >= threshold_accesses
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        if not self.access_counts:
            return {"total_keys": 0, "total_accesses": 0}
        
        total_accesses = sum(self.access_counts.values())
        avg_accesses = total_accesses / len(self.access_counts)
        
        return {
            "total_keys": len(self.access_counts),
            "total_accesses": total_accesses,
            "avg_accesses_per_key": round(avg_accesses, 2),
            "hot_keys": self.get_hot_keys(5)
        }

class BatchProcessor:
    """Processador de lotes para otimização"""
    
    def __init__(self, batch_size: int = 100, flush_interval: int = 30):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batches = defaultdict(list)
        self.last_flush = {}
    
    def add_item(self, batch_key: str, item: Any):
        """Adiciona item ao lote"""
        self.batches[batch_key].append(item)
        
        if batch_key not in self.last_flush:
            self.last_flush[batch_key] = time.time()
    
    def should_flush(self, batch_key: str) -> bool:
        """Determina se lote deve ser processado"""
        batch = self.batches.get(batch_key, [])
        last_flush = self.last_flush.get(batch_key, time.time())
        
        # Flush por tamanho ou tempo
        return (len(batch) >= self.batch_size or 
                time.time() - last_flush >= self.flush_interval)
    
    def get_batch(self, batch_key: str) -> List[Any]:
        """Retorna e limpa lote"""
        batch = self.batches.get(batch_key, [])
        self.batches[batch_key] = []
        self.last_flush[batch_key] = time.time()
        return batch

class PerformanceUtils:
    """Classe principal com utilitários de performance"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.cache_optimizer = CacheOptimizer()
        self.batch_processor = BatchProcessor()
        self.rate_limiters = {}
        
    def create_rate_limiter(self, name: str, max_calls: int, window_seconds: int) -> RateLimiter:
        """Cria rate limiter"""
        limiter = RateLimiter(max_calls, window_seconds)
        self.rate_limiters[name] = limiter
        return limiter
    
    def get_rate_limiter(self, name: str) -> Optional[RateLimiter]:
        """Retorna rate limiter"""
        return self.rate_limiters.get(name)
    
    def benchmark_function(self, func: Callable, iterations: int = 1000, *args, **kwargs) -> BenchmarkResult:
        """Executa benchmark de uma função"""
        times = []
        
        for _ in range(iterations):
            start_time = time.time()
            func(*args, **kwargs)
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        total_time = sum(times)
        avg_time = total_time / iterations
        ops_per_second = iterations / total_time if total_time > 0 else 0
        
        return BenchmarkResult(
            function_name=func.__name__,
            iterations=iterations,
            total_time=total_time,
            avg_time_per_iteration=avg_time,
            operations_per_second=ops_per_second,
            memory_peak_mb=0.0  # Implementação simplificada
        )
    
    def generate_cache_key(self, *args, **kwargs) -> str:
        """Gera chave de cache determinística"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance"""
        profiles = self.profiler.get_all_profiles()
        
        return {
            "profiler": {
                "total_functions": len(profiles),
                "total_calls": sum(p.call_count for p in profiles),
                "slowest_functions": sorted(profiles, key=lambda p: p.avg_time, reverse=True)[:5]
            },
            "cache_optimizer": self.cache_optimizer.get_cache_stats(),
            "rate_limiters": {
                name: {"calls_in_window": len(limiter.calls)}
                for name, limiter in self.rate_limiters.items()
            }
        }

# Singleton instance
performance_utils = PerformanceUtils()

# Decoradores úteis

def profile_performance(func):
    """Decorador para profiling automático"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        function_name = f"{func.__module__}.{func.__name__}"
        performance_utils.profiler.start_timing(function_name)
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            performance_utils.profiler.end_timing(function_name)
    
    return wrapper

def rate_limit(max_calls: int, window_seconds: int):
    """Decorador para rate limiting"""
    def decorator(func):
        function_name = f"{func.__module__}.{func.__name__}"
        limiter = performance_utils.create_rate_limiter(function_name, max_calls, window_seconds)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.is_allowed():
                wait_time = limiter.wait_time()
                raise Exception(f"Rate limit exceeded. Wait {wait_time:.2f}s")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def cached_result(ttl_seconds: int = 3600):
    """Decorador para cache de resultados"""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave
            cache_key = performance_utils.generate_cache_key(*args, **kwargs)
            
            # Verificar cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    performance_utils.cache_optimizer.record_access(cache_key)
                    return result
            
            # Executar função e cachear
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator 