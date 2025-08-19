"""In-memory caching utilities for subtitle content."""
import time
from typing import Any, Dict, Optional, Tuple
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class SubtitleCache:
    """Thread-safe in-memory cache for subtitle content with TTL support."""
    
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Initialize the subtitle cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
            max_size: Maximum number of cached items (default: 1000)
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, movie_id: int, language_id: int) -> str:
        """Generate cache key for movie-language combination."""
        return f"subtitles:{movie_id}:{language_id}"
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cached item has expired."""
        return time.time() > timestamp
    
    def _evict_expired(self) -> None:
        """Remove expired items from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time > expiry
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def _enforce_size_limit(self) -> None:
        """Remove oldest items if cache exceeds max size."""
        if len(self._cache) <= self.max_size:
            return
        
        # Sort by expiry time and remove oldest entries
        sorted_items = sorted(
            self._cache.items(),
            key=lambda item: item[1][1]  # Sort by expiry timestamp
        )
        
        # Keep only the newest max_size items
        items_to_remove = len(self._cache) - self.max_size
        for key, _ in sorted_items[:items_to_remove]:
            del self._cache[key]
    
    def get(self, movie_id: int, language_id: int) -> Optional[Any]:
        """
        Get cached subtitle content for movie-language combination.
        
        Args:
            movie_id: Movie ID
            language_id: Language ID
            
        Returns:
            Cached subtitle content or None if not found/expired
        """
        key = self._generate_key(movie_id, language_id)
        
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            content, expiry = self._cache[key]
            
            if self._is_expired(expiry):
                del self._cache[key]
                self._misses += 1
                return None
            
            self._hits += 1
            return content
    
    def set(self, movie_id: int, language_id: int, content: Any, ttl: Optional[int] = None) -> None:
        """
        Cache subtitle content for movie-language combination.
        
        Args:
            movie_id: Movie ID
            language_id: Language ID  
            content: Subtitle content to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        key = self._generate_key(movie_id, language_id)
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        
        with self._lock:
            self._cache[key] = (content, expiry)
            self._evict_expired()
            self._enforce_size_limit()
            
        logger.debug(f"Cached subtitles for movie {movie_id}, language {language_id}")
    
    def invalidate(self, movie_id: int, language_id: Optional[int] = None) -> None:
        """
        Invalidate cached subtitle content.
        
        Args:
            movie_id: Movie ID to invalidate
            language_id: Specific language ID to invalidate (if None, invalidates all languages for movie)
        """
        with self._lock:
            if language_id is not None:
                # Invalidate specific movie-language combination
                key = self._generate_key(movie_id, language_id)
                if key in self._cache:
                    del self._cache[key]
                    logger.debug(f"Invalidated cache for movie {movie_id}, language {language_id}")
            else:
                # Invalidate all languages for the movie
                prefix = f"subtitles:{movie_id}:"
                keys_to_remove = [key for key in self._cache.keys() if key.startswith(prefix)]
                for key in keys_to_remove:
                    del self._cache[key]
                logger.debug(f"Invalidated all cached subtitles for movie {movie_id}")
    
    def clear(self) -> None:
        """Clear all cached content."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
        logger.debug("Cleared all cached subtitle content")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self._hits,
                'misses': self._misses,
                'total_requests': total_requests,
                'hit_rate_percent': round(hit_rate, 2),
                'cache_size': len(self._cache),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl
            }
    
    def warm_cache(self, subtitle_data: Dict[Tuple[int, int], Any]) -> None:
        """
        Pre-populate cache with subtitle data.
        
        Args:
            subtitle_data: Dictionary mapping (movie_id, language_id) tuples to subtitle content
        """
        with self._lock:
            for (movie_id, language_id), content in subtitle_data.items():
                key = self._generate_key(movie_id, language_id)
                expiry = time.time() + self.default_ttl
                self._cache[key] = (content, expiry)
                
        logger.info(f"Warmed cache with {len(subtitle_data)} subtitle entries")


# Global cache instance
subtitle_cache = SubtitleCache()