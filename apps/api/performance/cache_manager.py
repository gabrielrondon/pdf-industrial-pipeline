"""
Intelligent Cache Manager - Stage 6 Performance

Gerencia cache Redis inteligente para melhorar performance:
- Cache de resultados ML (predições, features)
- Cache de embeddings e análises de texto
- Cache de respostas de API
- Políticas de TTL e invalidação
- Métricas de performance do cache
"""

import redis
import json
import hashlib
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pickle

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Estatísticas do cache"""
    total_keys: int
    hit_rate: float
    miss_rate: float
    memory_usage_mb: float
    avg_ttl_seconds: float
    most_accessed_keys: List[str]
    cache_efficiency: float

@dataclass
class CacheConfig:
    """Configuração do cache"""
    default_ttl: int = 3600  # 1 hora
    max_memory: int = 512    # 512MB
    eviction_policy: str = "allkeys-lru"
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 1  # DB separado para cache

class IntelligentCacheManager:
    """
    Gerenciador de cache inteligente com Redis
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.redis_client = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "start_time": datetime.now()
        }
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Inicializa conexão Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=False,  # Para suportar dados binários
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Testar conexão
            self.redis_client.ping()
            
            # Configurar políticas de memória
            self.redis_client.config_set('maxmemory', f'{self.config.max_memory}mb')
            self.redis_client.config_set('maxmemory-policy', self.config.eviction_policy)
            
            logger.info(f"Cache Redis inicializado: {self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}")
            
        except Exception as e:
            logger.error(f"Erro ao conectar Redis: {e}")
            self.redis_client = None
    
    def _generate_key(self, namespace: str, identifier: str, **kwargs) -> str:
        """Gera chave única para cache"""
        key_data = f"{namespace}:{identifier}"
        
        if kwargs:
            # Adicionar parâmetros extras à chave
            params = sorted(kwargs.items())
            params_str = "&".join(f"{k}={v}" for k, v in params)
            key_data += f":{params_str}"
        
        # Hash para garantir tamanho consistente
        return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def set(self, namespace: str, identifier: str, data: Any, 
            ttl: Optional[int] = None, **kwargs) -> bool:
        """
        Armazena dados no cache
        
        Args:
            namespace: Categoria do cache (ml_predictions, embeddings, etc.)
            identifier: Identificador único (job_id, query_hash, etc.)
            data: Dados para armazenar
            ttl: Tempo de vida em segundos
            **kwargs: Parâmetros extras para a chave
        """
        if not self.redis_client:
            return False
        
        try:
            key = self._generate_key(namespace, identifier, **kwargs)
            ttl = ttl or self.config.default_ttl
            
            # Serializar dados
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            else:
                serialized_data = pickle.dumps(data)
            
            # Armazenar com TTL
            result = self.redis_client.setex(key, ttl, serialized_data)
            
            if result:
                self.stats["sets"] += 1
                logger.debug(f"Cache SET: {namespace}:{identifier} (TTL: {ttl}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {e}")
            return False
    
    def get(self, namespace: str, identifier: str, **kwargs) -> Optional[Any]:
        """
        Recupera dados do cache
        
        Args:
            namespace: Categoria do cache
            identifier: Identificador único
            **kwargs: Parâmetros extras para a chave
        """
        if not self.redis_client:
            return None
        
        try:
            key = self._generate_key(namespace, identifier, **kwargs)
            serialized_data = self.redis_client.get(key)
            
            if serialized_data is None:
                self.stats["misses"] += 1
                logger.debug(f"Cache MISS: {namespace}:{identifier}")
                return None
            
            # Deserializar dados
            try:
                # Tentar JSON primeiro
                data = json.loads(serialized_data.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Usar pickle como fallback
                data = pickle.loads(serialized_data)
            
            self.stats["hits"] += 1
            logger.debug(f"Cache HIT: {namespace}:{identifier}")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao recuperar do cache: {e}")
            self.stats["misses"] += 1
            return None
    
    def delete(self, namespace: str, identifier: str, **kwargs) -> bool:
        """Remove item do cache"""
        if not self.redis_client:
            return False
        
        try:
            key = self._generate_key(namespace, identifier, **kwargs)
            result = self.redis_client.delete(key)
            
            if result:
                self.stats["deletes"] += 1
                logger.debug(f"Cache DELETE: {namespace}:{identifier}")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erro ao deletar do cache: {e}")
            return False
    
    def invalidate_namespace(self, namespace: str) -> int:
        """Invalida todos os itens de um namespace"""
        if not self.redis_client:
            return 0
        
        try:
            pattern = f"cache:*{namespace}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.stats["deletes"] += deleted
                logger.info(f"Cache namespace invalidado: {namespace} ({deleted} chaves)")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao invalidar namespace: {e}")
            return 0
    
    def get_stats(self) -> CacheStats:
        """Retorna estatísticas do cache"""
        if not self.redis_client:
            return CacheStats(0, 0, 0, 0, 0, [], 0)
        
        try:
            # Estatísticas básicas
            total_hits = self.stats["hits"]
            total_misses = self.stats["misses"]
            total_requests = total_hits + total_misses
            
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            miss_rate = (total_misses / total_requests * 100) if total_requests > 0 else 0
            
            # Informações do Redis
            info = self.redis_client.info()
            memory_usage_mb = info.get('used_memory', 0) / (1024 * 1024)
            
            # Contar chaves
            total_keys = self.redis_client.dbsize()
            
            # Chaves mais acessadas (simulado - Redis não tem essa métrica nativa)
            all_keys = self.redis_client.keys('cache:*')[:10]  # Primeiras 10
            most_accessed = [key.decode('utf-8') if isinstance(key, bytes) else key 
                           for key in all_keys]
            
            # TTL médio
            avg_ttl = 0
            if all_keys:
                ttls = [self.redis_client.ttl(key) for key in all_keys[:50]]  # Sample
                valid_ttls = [ttl for ttl in ttls if ttl > 0]
                avg_ttl = sum(valid_ttls) / len(valid_ttls) if valid_ttls else 0
            
            # Eficiência do cache
            cache_efficiency = hit_rate if total_requests > 100 else 0
            
            return CacheStats(
                total_keys=total_keys,
                hit_rate=round(hit_rate, 2),
                miss_rate=round(miss_rate, 2),
                memory_usage_mb=round(memory_usage_mb, 2),
                avg_ttl_seconds=round(avg_ttl, 0),
                most_accessed_keys=most_accessed,
                cache_efficiency=round(cache_efficiency, 2)
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return CacheStats(0, 0, 0, 0, 0, [], 0)
    
    def clear_all(self) -> bool:
        """Limpa todo o cache"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            logger.info("Cache completamente limpo")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do cache"""
        if not self.redis_client:
            return {
                "status": "unhealthy",
                "error": "Redis não conectado"
            }
        
        try:
            # Teste de conectividade
            latency_start = datetime.now()
            self.redis_client.ping()
            latency = (datetime.now() - latency_start).total_seconds() * 1000
            
            # Informações do servidor
            info = self.redis_client.info()
            
            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Singleton instance
cache_manager = IntelligentCacheManager()

# Decorador para cache automático
def cached(namespace: str, ttl: Optional[int] = None):
    """
    Decorador para cache automático de funções
    
    Usage:
        @cached("ml_predictions", ttl=3600)
        def predict_leads(job_id: str):
            # Expensive computation
            return results
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar identificador único baseado em argumentos
            args_str = str(args) + str(sorted(kwargs.items()))
            identifier = hashlib.md5(args_str.encode()).hexdigest()
            
            # Tentar cache primeiro
            cached_result = cache_manager.get(namespace, identifier)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache_manager.set(namespace, identifier, result, ttl)
            
            return result
        return wrapper
    return decorator 