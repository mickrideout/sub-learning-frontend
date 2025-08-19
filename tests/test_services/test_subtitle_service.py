"""Tests for subtitle service functionality."""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from app.services.subtitle_service import SubtitleService
from app.utils.cache import subtitle_cache


class TestSubtitleService:
    """Test cases for SubtitleService class."""

    @pytest.fixture(autouse=True)
    def setup_method(self, app):
        """Clear cache before each test and set up app context."""
        subtitle_cache.clear()
        self.app = app

    def test_get_subtitle_content_invalid_parameters(self):
        """Test subtitle content retrieval with invalid parameters."""
        # Test with missing movie_id
        with pytest.raises(ValueError, match="Both movie_id and language_id are required"):
            SubtitleService.get_subtitle_content(None, 1)
        
        # Test with missing language_id
        with pytest.raises(ValueError, match="Both movie_id and language_id are required"):
            SubtitleService.get_subtitle_content(1, None)
        
        # Test with zero movie_id
        with pytest.raises(ValueError, match="Both movie_id and language_id are required"):
            SubtitleService.get_subtitle_content(0, 1)

    @patch('app.services.subtitle_service.SubtitleService._movie_exists')
    @patch('app.services.subtitle_service.SubtitleService._language_exists')
    def test_get_subtitle_content_nonexistent_movie(self, mock_lang_exists, mock_movie_exists):
        """Test subtitle content retrieval with nonexistent movie."""
        mock_movie_exists.return_value = False
        mock_lang_exists.return_value = True
        
        with pytest.raises(ValueError, match="Movie with ID 999 not found"):
            SubtitleService.get_subtitle_content(999, 1)

    @patch('app.services.subtitle_service.SubtitleService._movie_exists')
    @patch('app.services.subtitle_service.SubtitleService._language_exists')
    def test_get_subtitle_content_nonexistent_language(self, mock_lang_exists, mock_movie_exists):
        """Test subtitle content retrieval with nonexistent language."""
        mock_movie_exists.return_value = True
        mock_lang_exists.return_value = False
        
        with pytest.raises(ValueError, match="Language with ID 999 not found"):
            SubtitleService.get_subtitle_content(1, 999)

    @patch('app.services.subtitle_service.db.engine.connect')
    @patch('app.services.subtitle_service.SubtitleService._movie_exists')
    @patch('app.services.subtitle_service.SubtitleService._language_exists')
    def test_get_subtitle_content_success(self, mock_lang_exists, mock_movie_exists, mock_connect):
        """Test successful subtitle content retrieval."""
        mock_movie_exists.return_value = True
        mock_lang_exists.return_value = True
        
        # Mock database response
        mock_row1 = MagicMock()
        mock_row1.id = 1
        mock_row1.sequence = 1
        mock_row1.content = "Hello world"
        mock_row1.language_id = 1
        
        mock_row2 = MagicMock()
        mock_row2.id = 2
        mock_row2.sequence = 2
        mock_row2.content = "How are you?"
        mock_row2.language_id = 1
        
        mock_result = [mock_row1, mock_row2]
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        result = SubtitleService.get_subtitle_content(123, 1)
        
        expected = [
            {'id': 1, 'sequence': 1, 'content': 'Hello world', 'language_id': 1},
            {'id': 2, 'sequence': 2, 'content': 'How are you?', 'language_id': 1}
        ]
        
        assert result == expected
        
        # Verify caching - second call should hit cache
        result2 = SubtitleService.get_subtitle_content(123, 1)
        assert result2 == expected
        
        # Database should only be called once due to caching
        mock_conn.execute.assert_called_once()

    @patch('app.services.subtitle_service.db.engine.connect')
    @patch('app.services.subtitle_service.SubtitleService._movie_exists')
    @patch('app.services.subtitle_service.SubtitleService._language_exists')
    def test_get_subtitle_content_database_error(self, mock_lang_exists, mock_movie_exists, mock_connect):
        """Test subtitle content retrieval with database error."""
        mock_movie_exists.return_value = True
        mock_lang_exists.return_value = True
        mock_connect.side_effect = SQLAlchemyError("Database connection failed")
        
        with pytest.raises(Exception, match="Database error while fetching subtitles"):
            SubtitleService.get_subtitle_content(123, 1)

    @patch('app.services.subtitle_service.db.engine.connect')
    @patch('app.services.subtitle_service.SubtitleService._movie_exists')
    def test_get_available_languages_success(self, mock_movie_exists, mock_connect):
        """Test successful available languages retrieval."""
        mock_movie_exists.return_value = True
        
        # Mock database response
        mock_row1 = MagicMock()
        mock_row1.language_id = 1
        mock_row1.language_name = "english"
        mock_row1.display_name = "English"
        
        mock_row2 = MagicMock()
        mock_row2.language_id = 2
        mock_row2.language_name = "spanish"
        mock_row2.display_name = "Spanish"
        
        mock_result = [mock_row1, mock_row2]
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_result
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        result = SubtitleService.get_available_languages(123)
        
        expected = [
            {'id': 1, 'name': 'english', 'display_name': 'English'},
            {'id': 2, 'name': 'spanish', 'display_name': 'Spanish'}
        ]
        
        assert result == expected

    def test_get_available_languages_invalid_movie_id(self):
        """Test available languages retrieval with invalid movie ID."""
        with pytest.raises(ValueError, match="movie_id is required"):
            SubtitleService.get_available_languages(None)
        
        with pytest.raises(ValueError, match="movie_id is required"):
            SubtitleService.get_available_languages(0)

    @patch('app.services.subtitle_service.db.engine.connect')
    def test_validate_subtitle_access_success(self, mock_connect):
        """Test successful subtitle access validation."""
        # Mock database response indicating access is allowed
        mock_result = MagicMock()
        mock_result.count = 1
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = mock_result
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        result = SubtitleService.validate_subtitle_access(123, 1, 1, 2)
        assert result is True

    @patch('app.services.subtitle_service.db.engine.connect')
    def test_validate_subtitle_access_denied(self, mock_connect):
        """Test subtitle access validation when access is denied."""
        # Mock database response indicating no access
        mock_result = MagicMock()
        mock_result.count = 0
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = mock_result
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        result = SubtitleService.validate_subtitle_access(123, 1, 1, 2)
        assert result is False

    def test_validate_subtitle_access_invalid_parameters(self):
        """Test subtitle access validation with invalid parameters."""
        # Test with missing parameters
        assert SubtitleService.validate_subtitle_access(None, 1, 1, 2) is False
        assert SubtitleService.validate_subtitle_access(123, None, 1, 2) is False
        assert SubtitleService.validate_subtitle_access(123, 1, None, 2) is False
        assert SubtitleService.validate_subtitle_access(123, 1, 1, None) is False
        
        # Test with language not in user's pair
        assert SubtitleService.validate_subtitle_access(123, 3, 1, 2) is False

    def test_invalidate_cache(self):
        """Test cache invalidation functionality."""
        # Add some content to cache
        subtitle_cache.set(123, 1, [{'id': 1}])
        subtitle_cache.set(123, 2, [{'id': 2}])
        
        # Verify content is cached
        assert subtitle_cache.get(123, 1) is not None
        assert subtitle_cache.get(123, 2) is not None
        
        # Invalidate specific language
        SubtitleService.invalidate_cache(123, 1)
        
        assert subtitle_cache.get(123, 1) is None
        assert subtitle_cache.get(123, 2) is not None
        
        # Invalidate all languages for movie
        SubtitleService.invalidate_cache(123)
        
        assert subtitle_cache.get(123, 2) is None

    def test_get_cache_stats(self):
        """Test cache statistics retrieval."""
        stats = SubtitleService.get_cache_stats()
        
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'total_requests' in stats
        assert 'hit_rate_percent' in stats
        assert 'cache_size' in stats

    @patch('app.services.subtitle_service.db.engine.connect')
    def test_movie_exists_true(self, mock_connect):
        """Test movie existence check returning True."""
        mock_result = MagicMock()
        mock_result.count = 1
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = mock_result
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        result = SubtitleService._movie_exists(123)
        assert result is True

    @patch('app.services.subtitle_service.db.engine.connect')
    def test_movie_exists_false(self, mock_connect):
        """Test movie existence check returning False."""
        mock_result = MagicMock()
        mock_result.count = 0
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = mock_result
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        result = SubtitleService._movie_exists(999)
        assert result is False

    @patch('app.services.subtitle_service.db.engine.connect')
    def test_movie_exists_database_error(self, mock_connect):
        """Test movie existence check with database error."""
        mock_connect.side_effect = SQLAlchemyError("Database error")
        
        result = SubtitleService._movie_exists(123)
        assert result is False

    def test_validate_subtitle_data_valid(self):
        """Test subtitle data validation with valid data."""
        valid_data = [
            {'id': 1, 'sequence': 1, 'content': 'Hello', 'language_id': 1},
            {'id': 2, 'sequence': 2, 'content': 'World', 'language_id': 1}
        ]
        
        result = SubtitleService.validate_subtitle_data(valid_data)
        assert result is True

    def test_validate_subtitle_data_invalid(self):
        """Test subtitle data validation with invalid data."""
        # Test with non-list input
        assert SubtitleService.validate_subtitle_data("not a list") is False
        
        # Test with non-dict items
        assert SubtitleService.validate_subtitle_data([1, 2, 3]) is False
        
        # Test with missing required fields
        invalid_data = [{'id': 1, 'sequence': 1}]  # Missing content and language_id
        assert SubtitleService.validate_subtitle_data(invalid_data) is False
        
        # Test with invalid field types
        invalid_data = [{'id': 'not_int', 'sequence': 1, 'content': 'Hello', 'language_id': 1}]
        assert SubtitleService.validate_subtitle_data(invalid_data) is False
        
        # Test with invalid sequence values
        invalid_data = [{'id': 1, 'sequence': -1, 'content': 'Hello', 'language_id': 1}]
        assert SubtitleService.validate_subtitle_data(invalid_data) is False
        
        # Test with empty content
        invalid_data = [{'id': 1, 'sequence': 1, 'content': '', 'language_id': 1}]
        assert SubtitleService.validate_subtitle_data(invalid_data) is False
        
        # Test with unordered sequences
        invalid_data = [
            {'id': 1, 'sequence': 2, 'content': 'Hello', 'language_id': 1},
            {'id': 2, 'sequence': 1, 'content': 'World', 'language_id': 1}
        ]
        assert SubtitleService.validate_subtitle_data(invalid_data) is False