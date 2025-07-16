import threading
import time
from collections import OrderedDict
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

class InMemoryCache:
    """
    Cost-optimized in-memory cache service as an alternative to Redis.
    Provides LRU eviction and TTL support.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.lock = threading.RLock()  # Reentrant lock for better performance
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"InMemoryCache initialized with max_size={max_size}, default_ttl={default_ttl}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with LRU update."""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if time.time() < item['expires_at']:
                    # Move to end (LRU)
                    self.cache.move_to_end(key)
                    self.stats['hits'] += 1
                    return item['value']
                else:
                    # Expired, remove
                    del self.cache[key]
                    self.stats['evictions'] += 1
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl
            
            # Remove if exists
            if key in self.cache:
                del self.cache[key]
            
            # Add new item
            self.cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            
            self.stats['sets'] += 1
            
            # Evict if over size limit
            if len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.stats['deletes'] += 1
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if time.time() < item['expires_at']:
                    return True
                else:
                    # Expired, remove
                    del self.cache[key]
                    self.stats['evictions'] += 1
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
    
    def _cleanup_expired(self) -> None:
        """Background thread to clean up expired entries."""
        while True:
            time.sleep(60)  # Cleanup every minute
            try:
                with self.lock:
                    current_time = time.time()
                    expired_keys = [
                        key for key, item in self.cache.items()
                        if current_time >= item['expires_at']
                    ]
                    
                    for key in expired_keys:
                        del self.cache[key]
                        self.stats['evictions'] += 1
                    
                    if expired_keys:
                        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                        
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")

# Global cache instance
cache = InMemoryCache(max_size=1000, default_ttl=300) 