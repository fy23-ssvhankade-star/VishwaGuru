import time
import logging
import threading
from typing import Any, Optional
from datetime import datetime, timedelta
from collections import OrderedDict

logger = logging.getLogger(__name__)

class ThreadSafeCache:
    """
    Thread-safe cache implementation with TTL and memory management.
    Uses OrderedDict for O(1) LRU eviction.
    """
    
    def __init__(self, ttl: int = 300, max_size: int = 100):
        self._data = OrderedDict()
        self._timestamps = {}
        self._ttl = ttl  # Time to live in seconds
        self._max_size = max_size  # Maximum number of cache entries
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
    def get(self, key: str = "default") -> Optional[Any]:
        """
        Thread-safe get operation with automatic cleanup.
        Optimized: Moves accessed item to end (MRU) in O(1).
        """
        with self._lock:
            current_time = time.time()
            
            # Check if key exists and is not expired
            if key in self._data:
                if current_time - self._timestamps[key] < self._ttl:
                    # Update access order for LRU (move to end = MRU)
                    self._data.move_to_end(key)
                    return self._data[key]
                else:
                    # Expired entry - remove it
                    self._remove_key(key)
            
            return None
    
    def set(self, data: Any, key: str = "default") -> None:
        """
        Thread-safe set operation with memory management.
        Optimized: O(1) eviction of LRU item when full.
        """
        with self._lock:
            current_time = time.time()
            
            # Clean up expired entries before adding new one
            self._cleanup_expired()
            
            # Update order if key exists
            if key in self._data:
                self._data.move_to_end(key)
            # If cache is full, evict the oldest item (least recently used)
            elif len(self._data) >= self._max_size:
                # popitem(last=False) removes the first (LRU) item in O(1)
                lru_key, _ = self._data.popitem(last=False)
                self._timestamps.pop(lru_key, None)
                logger.debug(f"Evicted LRU cache entry: {lru_key}")
            
            # Set new data atomically
            self._data[key] = data
            self._timestamps[key] = current_time
            
            logger.debug(f"Cache set: key={key}, size={len(self._data)}")
    
    def invalidate(self, key: str = "default") -> None:
        """
        Thread-safe invalidation of specific key.
        """
        with self._lock:
            self._remove_key(key)
            logger.debug(f"Cache invalidated: key={key}")
    
    def clear(self) -> None:
        """
        Thread-safe clear all cache entries.
        """
        with self._lock:
            self._data.clear()
            self._timestamps.clear()
            logger.debug("Cache cleared")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics for monitoring.
        """
        with self._lock:
            current_time = time.time()
            expired_count = sum(
                1 for ts in self._timestamps.values() 
                if current_time - ts >= self._ttl
            )
            
            return {
                "total_entries": len(self._data),
                "expired_entries": expired_count,
                "max_size": self._max_size,
                "ttl_seconds": self._ttl
            }
    
    def _remove_key(self, key: str) -> None:
        """
        Internal method to remove a key from all tracking dictionaries.
        Must be called within lock context.
        """
        self._data.pop(key, None)
        self._timestamps.pop(key, None)
    
    def _cleanup_expired(self) -> None:
        """
        Internal method to clean up expired entries.
        Must be called within lock context.
        """
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if current_time - timestamp >= self._ttl
        ]
        
        for key in expired_keys:
            self._remove_key(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    

class SimpleCache:
    """
    Backward compatibility wrapper for existing code.
    """
    
    def __init__(self, ttl: int = 60):
        self._cache = ThreadSafeCache(ttl=ttl, max_size=50)
    
    def get(self):
        return self._cache.get("default")
    
    def set(self, data):
        self._cache.set(data, "default")
    
    def invalidate(self):
        self._cache.invalidate("default")

# Global instances with improved configuration
recent_issues_cache = ThreadSafeCache(ttl=300, max_size=20)  # 5 minutes TTL, max 20 entries
nearby_issues_cache = ThreadSafeCache(ttl=60, max_size=100)  # 1 minute TTL, max 100 entries
user_upload_cache = ThreadSafeCache(ttl=3600, max_size=1000)  # 1 hour TTL for upload limits
