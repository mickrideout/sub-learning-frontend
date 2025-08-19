"""Tests for content service functionality."""
import pytest
from app.services.content_service import ContentService
from app.models import SubTitle, SubLink, Language
from app import db


class TestContentService:
    """Test cases for ContentService class."""

    def test_get_available_movies_with_valid_language_pair(self, app):
        """Test getting movies for a valid language pair."""
        with app.app_context():
            # The test data should already be loaded in the database
            # Test with English (1) to Spanish (2)
            movies = ContentService.get_available_movies(1, 2)
            
            assert isinstance(movies, list)
            assert len(movies) > 0
            
            # Check movie structure
            for movie in movies:
                assert 'id' in movie
                assert 'title' in movie
                assert 'subtitle_links_count' in movie
                assert 'has_subtitles' in movie
                assert movie['has_subtitles'] is True

    def test_get_available_movies_with_no_results(self, app):
        """Test getting movies for language pair with no available subtitles."""
        with app.app_context():
            # Use language IDs that don't have any subtitle links
            # German (4) to Italian (5) should have no movies based on our test data
            movies = ContentService.get_available_movies(4, 5)
            assert isinstance(movies, list)
            assert len(movies) == 0
            
    def test_get_available_movies_invalid_language_ids(self, app):
        """Test error handling for invalid language IDs."""
        with app.app_context():
            # Test with None values
            with pytest.raises(ValueError, match="Both native_language_id and target_language_id are required"):
                ContentService.get_available_movies(None, 2)
                
            with pytest.raises(ValueError, match="Both native_language_id and target_language_id are required"):
                ContentService.get_available_movies(1, None)

    def test_get_available_movies_same_language(self, app):
        """Test error handling when native and target languages are the same."""
        with app.app_context():
            with pytest.raises(ValueError, match="Native and target languages must be different"):
                ContentService.get_available_movies(1, 1)

    def test_get_movie_subtitle_info_valid_movie(self, app):
        """Test getting subtitle info for a valid movie and language pair."""
        with app.app_context():
            # Test with The Matrix (ID 1) for English to Spanish
            info = ContentService.get_movie_subtitle_info(1, 1, 2)
            
            assert info is not None
            assert info['movie_id'] == 1
            assert info['title'] == 'The Matrix'
            assert 'sub_link_id' in info
            assert 'from_language' in info
            assert 'to_language' in info

    def test_get_movie_subtitle_info_no_results(self, app):
        """Test getting subtitle info for movie with no available language pair."""
        with app.app_context():
            # Test with non-existent movie ID
            info = ContentService.get_movie_subtitle_info(999, 1, 2)
            assert info is None

    def test_validate_language_pair_valid(self, app):
        """Test language pair validation with valid languages."""
        with app.app_context():
            # Test with valid language IDs (1 and 2 should exist)
            assert ContentService.validate_language_pair(1, 2) is True

    def test_validate_language_pair_invalid(self, app):
        """Test language pair validation with invalid languages."""
        with app.app_context():
            # Test with non-existent language IDs
            assert ContentService.validate_language_pair(999, 1000) is False
            assert ContentService.validate_language_pair(1, 999) is False

    def test_get_available_movies_with_search_query(self, app):
        """Test getting movies with search query filtering."""
        with app.app_context():
            # Test searching for "Matrix" movies
            movies = ContentService.get_available_movies(1, 2, search_query="Matrix")
            
            assert isinstance(movies, list)
            # Should find The Matrix movie
            assert len(movies) > 0
            
            # All returned movies should contain "Matrix" in title (case-insensitive)
            for movie in movies:
                assert 'matrix' in movie['title'].lower()
                assert 'id' in movie
                assert 'title' in movie
                assert 'subtitle_links_count' in movie
                assert 'has_subtitles' in movie

    def test_get_available_movies_with_search_case_insensitive(self, app):
        """Test that search query is case-insensitive."""
        with app.app_context():
            # Test with different cases - should return same results
            movies_lower = ContentService.get_available_movies(1, 2, search_query="matrix")
            movies_upper = ContentService.get_available_movies(1, 2, search_query="MATRIX")
            movies_mixed = ContentService.get_available_movies(1, 2, search_query="Matrix")
            
            # All searches should return the same movies
            assert len(movies_lower) == len(movies_upper) == len(movies_mixed)
            
            # Convert to sets of movie IDs for comparison
            ids_lower = {movie['id'] for movie in movies_lower}
            ids_upper = {movie['id'] for movie in movies_upper}
            ids_mixed = {movie['id'] for movie in movies_mixed}
            
            assert ids_lower == ids_upper == ids_mixed

    def test_get_available_movies_with_search_partial_matching(self, app):
        """Test that search supports partial title matching."""
        with app.app_context():
            # Test partial matching - "Mat" should match "Matrix"
            movies_partial = ContentService.get_available_movies(1, 2, search_query="Mat")
            movies_full = ContentService.get_available_movies(1, 2, search_query="Matrix")
            
            assert isinstance(movies_partial, list)
            assert isinstance(movies_full, list)
            
            # Partial search should return at least as many results as full search
            # (since "Mat" is contained in "Matrix")
            assert len(movies_partial) >= len(movies_full)
            
            # All movies in full search should also be in partial search
            full_ids = {movie['id'] for movie in movies_full}
            partial_ids = {movie['id'] for movie in movies_partial}
            assert full_ids.issubset(partial_ids)

    def test_get_available_movies_with_search_no_results(self, app):
        """Test search query that returns no results."""
        with app.app_context():
            # Search for non-existent movie title
            movies = ContentService.get_available_movies(1, 2, search_query="NonExistentMovieTitle12345")
            
            assert isinstance(movies, list)
            assert len(movies) == 0

    def test_get_available_movies_with_empty_search_query(self, app):
        """Test that empty search query returns all movies."""
        with app.app_context():
            # Get all movies without search
            all_movies = ContentService.get_available_movies(1, 2)
            
            # Get movies with empty search query
            empty_search_movies = ContentService.get_available_movies(1, 2, search_query="")
            
            # Should return the same results
            assert len(all_movies) == len(empty_search_movies)
            
            # Convert to sets for comparison
            all_ids = {movie['id'] for movie in all_movies}
            empty_search_ids = {movie['id'] for movie in empty_search_movies}
            assert all_ids == empty_search_ids

    def test_get_available_movies_search_sql_injection_protection(self, app):
        """Test that search query is protected against SQL injection."""
        with app.app_context():
            # Try various SQL injection patterns
            malicious_queries = [
                "'; DROP TABLE sub_titles; --",
                "' OR '1'='1",
                "' UNION SELECT * FROM users --",
                "%'; DELETE FROM sub_titles; --"
            ]
            
            for malicious_query in malicious_queries:
                # Should not raise an exception and should return empty results
                # (since these aren't real movie titles)
                movies = ContentService.get_available_movies(1, 2, search_query=malicious_query)
                assert isinstance(movies, list)
                # Most likely empty results, but shouldn't crash

    def test_get_available_movies_search_special_characters(self, app):
        """Test search with special characters that need escaping."""
        with app.app_context():
            # Test with SQL wildcards that should be escaped
            special_queries = [
                "Movie%",
                "Movie_",
                "Movie%Title",
                "Movie_Title"
            ]
            
            for query in special_queries:
                # Should handle these gracefully without treating % and _ as wildcards
                movies = ContentService.get_available_movies(1, 2, search_query=query)
                assert isinstance(movies, list)
                # Results should only match literal text, not wildcard patterns