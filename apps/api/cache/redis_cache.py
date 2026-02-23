"""
Redis Cache Implementation for Performance Optimization
Specifically designed for caching dashboard stats and frequently accessed data
"""

import json
import redis
import logging
from typing import Optional, Any, Dict, Callable
from datetime import timedelta
from functools import wraps
import asyncio
import pickle

from config.settings import get_settings
from core.monitoring import cache_hits_total, cache_misses_total, track_cache_access

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisCache:
    """Redis cache implementation with monitoring integration"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = None
        self.is_connected = False
        self._connect()
    
    def _connect(self):
        """Establish Redis connection"""
        try:
            # Parse Redis URL to get connection params
            import urllib.parse
            parsed = urllib.parse.urlparse(settings.redis_url)
            
            self.redis_client = redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=int(parsed.path.strip('/')) if parsed.path else 2,
                password=parsed.password,
                decode_responses=False,  # We'll handle encoding
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 3,  # TCP_KEEPINTVL
                    3: 5   # TCP_KEEPCNT
                },
                retry_on_timeout=True,
                max_connections=10
            )
            
            # Test connection
            self.redis_client.ping()
            self.is_connected = True
            logger.info("✅ Redis cache connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis cache: {str(e)}")
            self.is_connected = False
    
    def _make_key(self, key: str, namespace: str = "cache") -> str:
        """Create namespaced cache key"""
        return f"{settings.environment}:{namespace}:{key}"
    
    def get(self, key: str, namespace: str = "cache") -> Optional[Any]:
        """Get value from cache"""
        if not self.is_connected:
            return None
            
        try:
            full_key = self._make_key(key, namespace)
            value = self.redis_client.get(full_key)
            
            if value is None:
                # Cache miss
                hit, miss = track_cache_access(namespace)
                miss()
                return None
            
            # Cache hit
            hit, miss = track_cache_access(namespace)
            hit()
            
            # Deserialize value
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Try pickle for complex objects
                return pickle.loads(value)
                
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300, namespace: str = "cache") -> bool:
        """Set value in cache with TTL in seconds"""
        if not self.is_connected:
            return False
            
        try:
            full_key = self._make_key(key, namespace)
            
            # Serialize value
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                # Fall back to pickle for complex objects
                serialized = pickle.dumps(value)
            
            # Set with expiration
            return self.redis_client.setex(full_key, ttl, serialized)
            
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str, namespace: str = "cache") -> bool:
        """Delete value from cache"""
        if not self.is_connected:
            return False
            
        try:
            full_key = self._make_key(key, namespace)
            return bool(self.redis_client.delete(full_key))
            
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear_namespace(self, namespace: str = "cache") -> int:
        """Clear all keys in a namespace"""
        if not self.is_connected:
            return 0
            
        try:
            pattern = f"{settings.environment}:{namespace}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                return self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return 0
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a specific user"""
        patterns = [
            f"dashboard_stats:{user_id}",
            f"user_jobs:{user_id}",
            f"user_documents:{user_id}"
        ]
        
        for pattern in patterns:
            self.delete(pattern, namespace="user")


# Global cache instance
cache = RedisCache()


def cached(ttl: int = 300, namespace: str = "cache", key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        namespace: Cache namespace for organization
        key_prefix: Additional prefix for the cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [key_prefix] if key_prefix else []
            cache_key_parts.append(func.__name__)
            
            # Add relevant args to cache key (skip DB session, etc)
            for arg in args[1:]:  # Skip self/cls
                if hasattr(arg, 'id'):
                    cache_key_parts.append(str(arg.id))
                elif isinstance(arg, (str, int, float, bool)):
                    cache_key_parts.append(str(arg))
            
            # Add relevant kwargs
            for k, v in sorted(kwargs.items()):
                if k not in ['db', 'session', 'request'] and isinstance(v, (str, int, float, bool)):
                    cache_key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_value = cache.get(cache_key, namespace)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)
            
            # Only cache non-None results
            if result is not None:
                cache.set(cache_key, result, ttl, namespace)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [key_prefix] if key_prefix else []
            cache_key_parts.append(func.__name__)
            
            # Add relevant args to cache key
            for arg in args[1:]:  # Skip self/cls
                if hasattr(arg, 'id'):
                    cache_key_parts.append(str(arg.id))
                elif isinstance(arg, (str, int, float, bool)):
                    cache_key_parts.append(str(arg))
            
            # Add relevant kwargs
            for k, v in sorted(kwargs.items()):
                if k not in ['db', 'session', 'request'] and isinstance(v, (str, int, float, bool)):
                    cache_key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_value = cache.get(cache_key, namespace)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)
            
            # Only cache non-None results
            if result is not None:
                cache.set(cache_key, result, ttl, namespace)
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Specific cache functions for common use cases
def cache_dashboard_stats(user_id: str, stats: Dict[str, Any], ttl: int = 300) -> bool:
    """Cache dashboard statistics for a user"""
    return cache.set(f"dashboard_stats:{user_id}", stats, ttl, namespace="user")


def get_cached_dashboard_stats(user_id: str) -> Optional[Dict[str, Any]]:
    """Get cached dashboard statistics for a user"""
    return cache.get(f"dashboard_stats:{user_id}", namespace="user")


def cache_job_list(user_id: str, jobs: list, ttl: int = 60) -> bool:
    """Cache job list for a user (shorter TTL for freshness)"""
    return cache.set(f"user_jobs:{user_id}", jobs, ttl, namespace="user")


def get_cached_job_list(user_id: str) -> Optional[list]:
    """Get cached job list for a user"""
    return cache.get(f"user_jobs:{user_id}", namespace="user")


def invalidate_user_stats(user_id: str):
    """Invalidate user statistics cache (call after new job/document)"""
    cache.delete(f"dashboard_stats:{user_id}", namespace="user")
    cache.delete(f"user_jobs:{user_id}", namespace="user")