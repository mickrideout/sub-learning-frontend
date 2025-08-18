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