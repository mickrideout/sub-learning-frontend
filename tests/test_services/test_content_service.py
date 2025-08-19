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

    def test_get_available_movies_with_letter_filter(self, app):
        """Test getting movies with letter filtering."""
        with app.app_context():
            # Test filtering by letter 'M' (should include "The Matrix")
            movies = ContentService.get_available_movies(1, 2, letter_filter="M")
            
            assert isinstance(movies, list)
            # All returned movies should start with 'M'
            for movie in movies:
                assert movie['title'][0].upper() == 'M'
                assert 'id' in movie
                assert 'title' in movie
                assert 'subtitle_links_count' in movie
                assert 'has_subtitles' in movie

    def test_get_available_movies_with_letter_filter_all(self, app):
        """Test letter filter with 'all' option."""
        with app.app_context():
            # Get all movies without filter
            all_movies = ContentService.get_available_movies(1, 2)
            
            # Get movies with 'all' filter
            all_filter_movies = ContentService.get_available_movies(1, 2, letter_filter="all")
            
            # Should return the same results
            assert len(all_movies) == len(all_filter_movies)
            
            # Convert to sets for comparison
            all_ids = {movie['id'] for movie in all_movies}
            all_filter_ids = {movie['id'] for movie in all_filter_movies}
            assert all_ids == all_filter_ids

    def test_get_available_movies_with_letter_filter_numbers(self, app):
        """Test letter filter with '#' for movies starting with numbers."""
        with app.app_context():
            # Test filtering by '#' for movies starting with numbers
            movies = ContentService.get_available_movies(1, 2, letter_filter="#")
            
            assert isinstance(movies, list)
            # All returned movies should start with a number
            for movie in movies:
                assert movie['title'][0].isdigit()

    def test_get_available_movies_with_letter_filter_case_insensitive(self, app):
        """Test that letter filtering is case-insensitive."""
        with app.app_context():
            # Test with both lowercase and uppercase
            movies_lower = ContentService.get_available_movies(1, 2, letter_filter="m")
            movies_upper = ContentService.get_available_movies(1, 2, letter_filter="M")
            
            # Should return the same results
            assert len(movies_lower) == len(movies_upper)
            
            # Convert to sets for comparison
            ids_lower = {movie['id'] for movie in movies_lower}
            ids_upper = {movie['id'] for movie in movies_upper}
            assert ids_lower == ids_upper

    def test_get_available_movies_with_search_and_letter_filter(self, app):
        """Test combining search query with letter filtering."""
        with app.app_context():
            # Test searching for "Matrix" and filtering by "M"
            movies = ContentService.get_available_movies(1, 2, search_query="Matrix", letter_filter="M")
            
            assert isinstance(movies, list)
            # All returned movies should contain "Matrix" AND start with "M"
            for movie in movies:
                assert 'matrix' in movie['title'].lower()
                assert movie['title'][0].upper() == 'M'

    def test_get_available_movies_invalid_letter_filter(self, app):
        """Test error handling for invalid letter filter."""
        with app.app_context():
            # Test with invalid letter filter values
            invalid_filters = ['XY', '1', '@', '', 'ALL', 'abc']
            
            for invalid_filter in invalid_filters:
                with pytest.raises(ValueError, match="Letter filter must be A-Z, #, or 'all'"):
                    ContentService.get_available_movies(1, 2, letter_filter=invalid_filter)

    def test_get_letter_counts(self, app):
        """Test getting letter counts for available movies."""
        with app.app_context():
            # Get letter counts for English to Spanish
            letter_counts = ContentService.get_letter_counts(1, 2)
            
            assert isinstance(letter_counts, dict)
            
            # Check that all letters A-Z and # are represented (some might be 0)
            expected_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ#')
            # At least some letters should have counts > 0
            assert len(letter_counts) > 0
            
            # All values should be non-negative integers
            for letter, count in letter_counts.items():
                assert letter in expected_letters
                assert isinstance(count, int)
                assert count >= 0

    def test_get_letter_counts_with_search_query(self, app):
        """Test getting letter counts with search query filtering."""
        with app.app_context():
            # Get letter counts with search query
            letter_counts = ContentService.get_letter_counts(1, 2, search_query="Matrix")
            
            assert isinstance(letter_counts, dict)
            
            # Should only have counts for letters that start movies matching "Matrix"
            total_matches = sum(letter_counts.values())
            
            # Get actual movies with same search to verify consistency
            movies = ContentService.get_available_movies(1, 2, search_query="Matrix")
            assert total_matches == len(movies)

    def test_get_letter_counts_invalid_language_ids(self, app):
        """Test error handling for invalid language IDs in letter counts."""
        with app.app_context():
            # Test with None values
            with pytest.raises(ValueError, match="Both native_language_id and target_language_id are required"):
                ContentService.get_letter_counts(None, 2)
                
            with pytest.raises(ValueError, match="Both native_language_id and target_language_id are required"):
                ContentService.get_letter_counts(1, None)

    def test_get_letter_counts_same_language(self, app):
        """Test error handling when native and target languages are the same for letter counts."""
        with app.app_context():
            with pytest.raises(ValueError, match="Native and target languages must be different"):
                ContentService.get_letter_counts(1, 1)

    def test_is_valid_letter_filter(self, app):
        """Test letter filter validation method."""
        with app.app_context():
            # Valid letters
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                assert ContentService._is_valid_letter_filter(letter) is True
                assert ContentService._is_valid_letter_filter(letter.lower()) is True
            
            # Valid special case
            assert ContentService._is_valid_letter_filter('#') is True
            
            # Invalid cases
            invalid_filters = ['', 'XY', '1', '@', 'ALL', 'abc', None, '##', 'A1']
            for invalid_filter in invalid_filters:
                assert ContentService._is_valid_letter_filter(invalid_filter) is False