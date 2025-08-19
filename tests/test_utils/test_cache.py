"""Tests for subtitle caching utilities."""
import pytest
import time
from unittest.mock import patch
from app.utils.cache import SubtitleCache


class TestSubtitleCache:
    """Test cases for SubtitleCache class."""

    @pytest.fixture
    def cache(self):
        """Create a fresh cache instance for testing."""
        return SubtitleCache(default_ttl=60, max_size=10)

    def test_cache_initialization(self, cache):
        """Test cache initialization with custom parameters."""
        assert cache.default_ttl == 60
        assert cache.max_size == 10
        assert cache._hits == 0
        assert cache._misses == 0
        assert len(cache._cache) == 0

    def test_cache_key_generation(self, cache):
        """Test cache key generation for movie-language combinations."""
        key1 = cache._generate_key(123, 456)
        key2 = cache._generate_key(123, 789)
        key3 = cache._generate_key(456, 123)
        
        assert key1 == "subtitles:123:456"
        assert key2 == "subtitles:123:789"
        assert key3 == "subtitles:456:123"
        assert key1 != key2
        assert key1 != key3

    def test_cache_set_and_get(self, cache):
        """Test basic cache set and get operations."""
        movie_id = 123
        language_id = 456
        content = [{'id': 1, 'sequence': 1, 'content': 'Hello', 'language_id': 456}]
        
        # Initially cache should be empty
        result = cache.get(movie_id, language_id)
        assert result is None
        assert cache._misses == 1
        assert cache._hits == 0
        
        # Set content in cache
        cache.set(movie_id, language_id, content)
        
        # Retrieve content from cache
        result = cache.get(movie_id, language_id)
        assert result == content
        assert cache._hits == 1
        assert cache._misses == 1

    def test_cache_expiry(self, cache):
        """Test cache expiry functionality."""
        movie_id = 123
        language_id = 456
        content = [{'id': 1, 'sequence': 1, 'content': 'Hello', 'language_id': 456}]
        
        # Set content with very short TTL
        cache.set(movie_id, language_id, content, ttl=1)
        
        # Should be available immediately
        result = cache.get(movie_id, language_id)
        assert result == content
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should be expired now
        result = cache.get(movie_id, language_id)
        assert result is None
        assert cache._misses == 1

    def test_cache_invalidation_specific(self, cache):
        """Test invalidating specific movie-language combination."""
        movie_id = 123
        language_id1 = 456
        language_id2 = 789
        content1 = [{'id': 1, 'sequence': 1, 'content': 'Hello', 'language_id': 456}]
        content2 = [{'id': 2, 'sequence': 1, 'content': 'Hola', 'language_id': 789}]
        
        # Set content for both languages
        cache.set(movie_id, language_id1, content1)
        cache.set(movie_id, language_id2, content2)
        
        # Verify both are cached
        assert cache.get(movie_id, language_id1) == content1
        assert cache.get(movie_id, language_id2) == content2
        
        # Invalidate only language_id1
        cache.invalidate(movie_id, language_id1)
        
        # Only language_id1 should be invalidated
        assert cache.get(movie_id, language_id1) is None
        assert cache.get(movie_id, language_id2) == content2

    def test_cache_invalidation_all_languages(self, cache):
        """Test invalidating all languages for a movie."""
        movie_id = 123
        language_id1 = 456
        language_id2 = 789
        content1 = [{'id': 1, 'sequence': 1, 'content': 'Hello', 'language_id': 456}]
        content2 = [{'id': 2, 'sequence': 1, 'content': 'Hola', 'language_id': 789}]
        
        # Set content for both languages
        cache.set(movie_id, language_id1, content1)
        cache.set(movie_id, language_id2, content2)
        
        # Verify both are cached
        assert cache.get(movie_id, language_id1) == content1
        assert cache.get(movie_id, language_id2) == content2
        
        # Invalidate all languages for movie
        cache.invalidate(movie_id)
        
        # Both should be invalidated
        assert cache.get(movie_id, language_id1) is None
        assert cache.get(movie_id, language_id2) is None

    def test_cache_clear(self, cache):
        """Test clearing entire cache."""
        # Add multiple items
        cache.set(123, 456, [{'id': 1}])
        cache.set(123, 789, [{'id': 2}])
        cache.set(456, 123, [{'id': 3}])
        
        # Verify items are cached
        assert cache.get(123, 456) is not None
        assert cache.get(123, 789) is not None
        assert cache.get(456, 123) is not None
        
        # Clear cache (this resets hits and misses to 0)
        cache.clear()
        
        # All items should be gone and stats should be reset
        assert cache.get(123, 456) is None
        assert cache.get(123, 789) is None
        assert cache.get(456, 123) is None
        # After clear(), hits and misses are reset, but the gets above will increment misses
        assert cache._hits == 0
        assert cache._misses == 3  # Three misses from the gets above

    def test_cache_size_limit(self, cache):
        """Test cache size limit enforcement."""
        # Fill cache beyond max_size (10)
        for i in range(15):
            cache.set(i, 1, [{'id': i}])
        
        # Cache should not exceed max_size
        assert len(cache._cache) <= cache.max_size

    def test_cache_stats(self, cache):
        """Test cache statistics collection."""
        movie_id = 123
        language_id = 456
        content = [{'id': 1}]
        
        # Initial stats
        stats = cache.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['total_requests'] == 0
        assert stats['hit_rate_percent'] == 0
        assert stats['cache_size'] == 0
        assert stats['max_size'] == 10
        assert stats['default_ttl'] == 60
        
        # Add some cache activity
        cache.get(movie_id, language_id)  # miss
        cache.set(movie_id, language_id, content)
        cache.get(movie_id, language_id)  # hit
        cache.get(movie_id, language_id)  # hit
        
        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['total_requests'] == 3
        assert stats['hit_rate_percent'] == 66.67
        assert stats['cache_size'] == 1

    def test_cache_warm_up(self, cache):
        """Test cache warming functionality."""
        warm_data = {
            (123, 456): [{'id': 1, 'content': 'Hello'}],
            (123, 789): [{'id': 2, 'content': 'Hola'}],
            (456, 123): [{'id': 3, 'content': 'Bonjour'}]
        }
        
        # Warm the cache
        cache.warm_cache(warm_data)
        
        # Verify all items are cached
        for (movie_id, language_id), expected_content in warm_data.items():
            result = cache.get(movie_id, language_id)
            assert result == expected_content
        
        # All should be cache hits
        stats = cache.get_stats()
        assert stats['hits'] == 3
        assert stats['misses'] == 0

    def test_cache_thread_safety(self, cache):
        """Test basic thread safety with locks."""
        import threading
        
        def cache_operations():
            for i in range(10):
                cache.set(i, 1, [{'id': i}])
                cache.get(i, 1)
        
        # Run multiple threads concurrently
        threads = [threading.Thread(target=cache_operations) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Cache should still be in valid state
        stats = cache.get_stats()
        assert stats['hits'] >= 0
        assert stats['misses'] >= 0
        assert len(cache._cache) <= cache.max_size

    def test_expired_item_cleanup(self, cache):
        """Test automatic cleanup of expired items."""
        # Add items with different TTLs
        cache.set(123, 456, [{'id': 1}], ttl=1)  # Expires quickly
        cache.set(456, 789, [{'id': 2}], ttl=60)  # Expires later
        
        # Wait for first item to expire
        time.sleep(1.1)
        
        # Add another item (should trigger cleanup)
        cache.set(789, 123, [{'id': 3}], ttl=60)
        
        # Expired item should be cleaned up, non-expired should remain
        assert cache.get(123, 456) is None  # Expired
        assert cache.get(456, 789) is not None  # Still valid
        assert cache.get(789, 123) is not None  # Still valid