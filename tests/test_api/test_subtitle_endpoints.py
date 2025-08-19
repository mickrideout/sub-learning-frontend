"""Tests for subtitle API endpoints."""
import pytest
import json
from unittest.mock import patch, MagicMock
from flask import url_for
from app.services.subtitle_service import SubtitleService


class TestSubtitleEndpoints:
    """Test cases for subtitle API endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        user = MagicMock()
        user.id = 1
        user.native_language_id = 1
        user.target_language_id = 2
        user.is_authenticated = True
        return user

    @pytest.fixture
    def mock_user_no_languages(self):
        """Create a mock user without language preferences."""
        user = MagicMock()
        user.id = 1
        user.native_language_id = None
        user.target_language_id = None
        user.is_authenticated = True
        return user

    def test_get_movie_subtitles_unauthenticated(self, client):
        """Test subtitle retrieval without authentication."""
        response = client.get('/api/movies/123/subtitles?lang=1')
        assert response.status_code == 401

    @patch('app.blueprints.api.subtitles.current_user')
    def test_get_movie_subtitles_invalid_movie_id(self, mock_current_user, client, mock_user):
        """Test subtitle retrieval with invalid movie ID."""
        mock_current_user.return_value = mock_user
        
        with client.application.test_request_context():
            with patch('flask_login.utils._get_user') as mock_get_user:
                mock_get_user.return_value = mock_user
                response = client.get('/api/movies/0/subtitles?lang=1')
                assert response.status_code == 400
                data = json.loads(response.data)
                assert data['code'] == 'INVALID_MOVIE_ID'

    @patch('app.blueprints.api.subtitles.current_user')
    def test_get_movie_subtitles_missing_language_parameter(self, mock_current_user, client, mock_user):
        """Test subtitle retrieval without language parameter."""
        mock_current_user.return_value = mock_user
        
        response = client.get('/api/movies/123/subtitles')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'MISSING_LANGUAGE_PARAMETER'

    @patch('app.blueprints.api.subtitles.current_user')
    def test_get_movie_subtitles_invalid_language_parameter(self, mock_current_user, client, mock_user):
        """Test subtitle retrieval with invalid language parameter."""
        mock_current_user.return_value = mock_user
        
        # Test with non-integer language parameter
        response = client.get('/api/movies/123/subtitles?lang=invalid')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'INVALID_LANGUAGE_ID'
        
        # Test with negative language ID
        response = client.get('/api/movies/123/subtitles?lang=-1')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'INVALID_LANGUAGE_ID'

    @patch('app.blueprints.api.subtitles.current_user')
    def test_get_movie_subtitles_no_user_languages(self, mock_current_user, client, mock_user_no_languages):
        """Test subtitle retrieval with user having no language preferences."""
        mock_current_user.return_value = mock_user_no_languages
        
        response = client.get('/api/movies/123/subtitles?lang=1')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'MISSING_LANGUAGE_PREFERENCES'

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.validate_subtitle_access')
    def test_get_movie_subtitles_access_denied(self, mock_validate_access, mock_current_user, client, mock_user):
        """Test subtitle retrieval with access denied."""
        mock_current_user.return_value = mock_user
        mock_validate_access.return_value = False
        
        response = client.get('/api/movies/123/subtitles?lang=1')
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['code'] == 'ACCESS_DENIED'

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.validate_subtitle_access')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_subtitle_content')
    def test_get_movie_subtitles_not_found(self, mock_get_content, mock_validate_access, mock_current_user, client, mock_user):
        """Test subtitle retrieval when subtitles not found."""
        mock_current_user.return_value = mock_user
        mock_validate_access.return_value = True
        mock_get_content.return_value = []  # Empty list
        
        response = client.get('/api/movies/123/subtitles?lang=1')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['code'] == 'SUBTITLES_NOT_FOUND'

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.validate_subtitle_access')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_subtitle_content')
    @patch('app.blueprints.api.subtitles.SubtitleService.validate_subtitle_data')
    def test_get_movie_subtitles_data_integrity_error(self, mock_validate_data, mock_get_content, mock_validate_access, mock_current_user, client, mock_user):
        """Test subtitle retrieval with data integrity error."""
        mock_current_user.return_value = mock_user
        mock_validate_access.return_value = True
        mock_get_content.return_value = [{'id': 1}]  # Some content
        mock_validate_data.return_value = False  # Invalid data
        
        response = client.get('/api/movies/123/subtitles?lang=1')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['code'] == 'DATA_INTEGRITY_ERROR'

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.validate_subtitle_access')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_subtitle_content')
    @patch('app.blueprints.api.subtitles.SubtitleService.validate_subtitle_data')
    def test_get_movie_subtitles_success(self, mock_validate_data, mock_get_content, mock_validate_access, mock_current_user, client, mock_user):
        """Test successful subtitle retrieval."""
        mock_current_user.return_value = mock_user
        mock_validate_access.return_value = True
        mock_validate_data.return_value = True
        
        subtitle_lines = [
            {'id': 1, 'sequence': 1, 'content': 'Hello world', 'language_id': 1},
            {'id': 2, 'sequence': 2, 'content': 'How are you?', 'language_id': 1}
        ]
        mock_get_content.return_value = subtitle_lines
        
        response = client.get('/api/movies/123/subtitles?lang=1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['movie_id'] == 123
        assert data['language_id'] == 1
        assert data['subtitle_lines'] == subtitle_lines
        assert data['total_lines'] == 2
        assert data['user_language_pair']['native_language_id'] == 1
        assert data['user_language_pair']['target_language_id'] == 2
        
        # Check caching headers
        assert 'Cache-Control' in response.headers
        assert 'ETag' in response.headers

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.validate_subtitle_access')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_subtitle_content')
    def test_get_movie_subtitles_service_error(self, mock_get_content, mock_validate_access, mock_current_user, client, mock_user):
        """Test subtitle retrieval with service error."""
        mock_current_user.return_value = mock_user
        mock_validate_access.return_value = True
        mock_get_content.side_effect = Exception("Database error")
        
        response = client.get('/api/movies/123/subtitles?lang=1')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['code'] == 'INTERNAL_ERROR'

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.validate_subtitle_access')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_subtitle_content')
    def test_get_movie_subtitles_validation_error(self, mock_get_content, mock_validate_access, mock_current_user, client, mock_user):
        """Test subtitle retrieval with validation error."""
        mock_current_user.return_value = mock_user
        mock_validate_access.return_value = True
        mock_get_content.side_effect = ValueError("Movie not found")
        
        response = client.get('/api/movies/123/subtitles?lang=1')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'VALIDATION_ERROR'

    def test_get_subtitle_availability_unauthenticated(self, client):
        """Test subtitle availability check without authentication."""
        response = client.get('/api/movies/123/subtitles/availability')
        assert response.status_code == 401

    @patch('app.blueprints.api.subtitles.current_user')
    def test_get_subtitle_availability_invalid_movie_id(self, mock_current_user, client, mock_user):
        """Test subtitle availability check with invalid movie ID."""
        mock_current_user.return_value = mock_user
        
        response = client.get('/api/movies/-1/subtitles/availability')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'INVALID_MOVIE_ID'

    @patch('app.blueprints.api.subtitles.current_user')
    def test_get_subtitle_availability_no_user_languages(self, mock_current_user, client, mock_user_no_languages):
        """Test subtitle availability check with user having no language preferences."""
        mock_current_user.return_value = mock_user_no_languages
        
        response = client.get('/api/movies/123/subtitles/availability')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'MISSING_LANGUAGE_PREFERENCES'

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_available_languages')
    def test_get_subtitle_availability_success(self, mock_get_languages, mock_current_user, client, mock_user):
        """Test successful subtitle availability check."""
        mock_current_user.return_value = mock_user
        
        available_languages = [
            {'id': 1, 'name': 'english', 'display_name': 'English'},
            {'id': 2, 'name': 'spanish', 'display_name': 'Spanish'},
            {'id': 3, 'name': 'french', 'display_name': 'French'}  # User doesn't have access to this
        ]
        mock_get_languages.return_value = available_languages
        
        response = client.get('/api/movies/123/subtitles/availability')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['movie_id'] == 123
        assert data['total_available'] == 2  # Only languages 1 and 2 accessible to user
        assert data['has_subtitles'] is True
        assert len(data['available_languages']) == 2
        
        # Check that only user's languages are included
        accessible_ids = {lang['id'] for lang in data['available_languages']}
        assert accessible_ids == {1, 2}

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_available_languages')
    def test_get_subtitle_availability_no_accessible_languages(self, mock_get_languages, mock_current_user, client, mock_user):
        """Test subtitle availability check with no accessible languages."""
        mock_current_user.return_value = mock_user
        
        # Return languages that user doesn't have access to
        available_languages = [
            {'id': 3, 'name': 'french', 'display_name': 'French'},
            {'id': 4, 'name': 'german', 'display_name': 'German'}
        ]
        mock_get_languages.return_value = available_languages
        
        response = client.get('/api/movies/123/subtitles/availability')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['movie_id'] == 123
        assert data['total_available'] == 0
        assert data['has_subtitles'] is False
        assert len(data['available_languages']) == 0

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_available_languages')
    def test_get_subtitle_availability_service_error(self, mock_get_languages, mock_current_user, client, mock_user):
        """Test subtitle availability check with service error."""
        mock_current_user.return_value = mock_user
        mock_get_languages.side_effect = Exception("Database error")
        
        response = client.get('/api/movies/123/subtitles/availability')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['code'] == 'INTERNAL_ERROR'

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_available_languages')
    def test_get_subtitle_availability_validation_error(self, mock_get_languages, mock_current_user, client, mock_user):
        """Test subtitle availability check with validation error."""
        mock_current_user.return_value = mock_user
        mock_get_languages.side_effect = ValueError("Movie not found")
        
        response = client.get('/api/movies/123/subtitles/availability')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'VALIDATION_ERROR'

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_cache_stats')
    def test_get_cache_stats_success(self, mock_get_stats, mock_current_user, client, mock_user):
        """Test successful cache statistics retrieval."""
        mock_current_user.return_value = mock_user
        
        cache_stats = {
            'hits': 100,
            'misses': 20,
            'total_requests': 120,
            'hit_rate_percent': 83.33,
            'cache_size': 50,
            'max_size': 1000,
            'default_ttl': 3600
        }
        mock_get_stats.return_value = cache_stats
        
        response = client.get('/api/subtitles/cache/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['cache_statistics'] == cache_stats

    def test_get_cache_stats_unauthenticated(self, client):
        """Test cache statistics retrieval without authentication."""
        response = client.get('/api/subtitles/cache/stats')
        assert response.status_code == 401

    @patch('app.blueprints.api.subtitles.current_user')
    @patch('app.blueprints.api.subtitles.SubtitleService.get_cache_stats')
    def test_get_cache_stats_service_error(self, mock_get_stats, mock_current_user, client, mock_user):
        """Test cache statistics retrieval with service error."""
        mock_current_user.return_value = mock_user
        mock_get_stats.side_effect = Exception("Cache error")
        
        response = client.get('/api/subtitles/cache/stats')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['code'] == 'INTERNAL_ERROR'