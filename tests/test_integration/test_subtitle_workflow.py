"""Integration tests for subtitle retrieval workflow."""
import pytest
from flask import url_for
from app import db
from app.models.subtitle import SubTitle, SubLine, SubLink
from app.models.language import Language
from app.models.user import User


class TestSubtitleWorkflowIntegration:
    """Integration tests for complete subtitle retrieval workflow."""

    @pytest.fixture
    def sample_data(self, app):
        """Create sample data for testing."""
        with app.app_context():
            # Create languages
            english = Language(id=1, name='english', display_name='English', code='en')
            spanish = Language(id=2, name='spanish', display_name='Spanish', code='es')
            french = Language(id=3, name='french', display_name='French', code='fr')
            
            db.session.add_all([english, spanish, french])
            
            # Create movies
            movie1 = SubTitle(id=1, title='Test Movie 1')
            movie2 = SubTitle(id=2, title='Test Movie 2')
            
            db.session.add_all([movie1, movie2])
            
            # Create subtitle links
            link1 = SubLink(id=1, fromid=1, fromlang=1, toid=1, tolang=2)  # English to Spanish
            link2 = SubLink(id=2, fromid=2, fromlang=2, toid=2, tolang=1)  # Spanish to English
            
            db.session.add_all([link1, link2])
            
            # Create subtitle lines for movie 1 in English
            lines_en = [
                SubLine(id=1, movie_id=1, sequence=1, content='Hello world', language_id=1),
                SubLine(id=2, movie_id=1, sequence=2, content='How are you?', language_id=1),
                SubLine(id=3, movie_id=1, sequence=3, content='Good morning', language_id=1)
            ]
            
            # Create subtitle lines for movie 1 in Spanish
            lines_es = [
                SubLine(id=4, movie_id=1, sequence=1, content='Hola mundo', language_id=2),
                SubLine(id=5, movie_id=1, sequence=2, content='¿Cómo estás?', language_id=2),
                SubLine(id=6, movie_id=1, sequence=3, content='Buenos días', language_id=2)
            ]
            
            # Create subtitle lines for movie 2 in Spanish
            lines_movie2 = [
                SubLine(id=7, movie_id=2, sequence=1, content='Bienvenido', language_id=2),
                SubLine(id=8, movie_id=2, sequence=2, content='Gracias', language_id=2)
            ]
            
            db.session.add_all(lines_en + lines_es + lines_movie2)
            
            # Create test user
            user = User(
                id=1,
                email='test@example.com',
                native_language_id=1,  # English
                target_language_id=2   # Spanish
            )
            user.set_password('testpassword')
            
            db.session.add(user)
            db.session.commit()

    def test_complete_subtitle_retrieval_workflow(self, client, sample_data):
        """Test complete workflow from login to subtitle retrieval."""
        # Login user
        login_response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        assert login_response.status_code in [200, 302]  # Success or redirect
        
        # Test subtitle retrieval for movie 1 in English
        response = client.get('/api/movies/1/subtitles?lang=1')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['movie_id'] == 1
        assert data['language_id'] == 1
        assert data['total_lines'] == 3
        assert len(data['subtitle_lines']) == 3
        
        # Verify subtitle content and ordering
        lines = data['subtitle_lines']
        assert lines[0]['sequence'] == 1
        assert lines[0]['content'] == 'Hello world'
        assert lines[1]['sequence'] == 2
        assert lines[1]['content'] == 'How are you?'
        assert lines[2]['sequence'] == 3
        assert lines[2]['content'] == 'Good morning'

    def test_subtitle_availability_check_workflow(self, client, sample_data):
        """Test subtitle availability checking workflow."""
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # Check availability for movie 1
        response = client.get('/api/movies/1/subtitles/availability')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['movie_id'] == 1
        assert data['has_subtitles'] is True
        assert data['total_available'] == 2  # English and Spanish
        
        # Verify available languages are user's languages
        available_ids = {lang['id'] for lang in data['available_languages']}
        assert available_ids == {1, 2}  # English and Spanish

    def test_access_control_workflow(self, client, sample_data):
        """Test access control for subtitles not in user's language pair."""
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # Try to access French subtitles (not in user's language pair)
        response = client.get('/api/movies/1/subtitles?lang=3')  # French
        assert response.status_code == 403
        
        data = response.get_json()
        assert data['code'] == 'ACCESS_DENIED'

    def test_movie_catalog_integration(self, client, sample_data):
        """Test integration with existing movie catalog functionality."""
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # Get available movies (should include subtitle availability)
        response = client.get('/api/movies')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'movies' in data
        assert data['total_count'] >= 1  # At least our test movie should be available

    def test_caching_performance_workflow(self, client, sample_data):
        """Test caching performance in realistic scenario."""
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # First request - should hit database
        response1 = client.get('/api/movies/1/subtitles?lang=1')
        assert response1.status_code == 200
        
        # Second request - should hit cache
        response2 = client.get('/api/movies/1/subtitles?lang=1')
        assert response2.status_code == 200
        
        # Responses should be identical
        assert response1.get_json() == response2.get_json()
        
        # Check cache statistics
        cache_response = client.get('/api/subtitles/cache/stats')
        assert cache_response.status_code == 200
        
        cache_data = cache_response.get_json()
        stats = cache_data['cache_statistics']
        assert stats['hits'] >= 1  # At least one cache hit
        assert stats['cache_size'] >= 1  # At least one item cached

    def test_error_handling_workflow(self, client, sample_data):
        """Test error handling in realistic scenarios."""
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # Test with nonexistent movie
        response = client.get('/api/movies/999/subtitles?lang=1')
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'VALIDATION_ERROR'
        
        # Test with invalid language parameter
        response = client.get('/api/movies/1/subtitles?lang=invalid')
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'INVALID_LANGUAGE_ID'
        
        # Test availability for nonexistent movie
        response = client.get('/api/movies/999/subtitles/availability')
        assert response.status_code == 400

    def test_concurrent_access_workflow(self, client, sample_data):
        """Test concurrent access to subtitle endpoints."""
        import threading
        import time
        
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        results = []
        
        def make_request():
            """Make subtitle request in thread."""
            try:
                response = client.get('/api/movies/1/subtitles?lang=1')
                results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
        
        # Create multiple threads for concurrent requests
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(result == 200 for result in results)

    def test_language_pair_filtering_workflow(self, client, sample_data):
        """Test that language pair filtering works correctly."""
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # User has English (1) and Spanish (2) as language pair
        # Movie 1 has subtitles in both languages
        # Movie 2 only has Spanish subtitles
        
        # Check availability for movie 1 - should show both languages
        response = client.get('/api/movies/1/subtitles/availability')
        data = response.get_json()
        available_ids = {lang['id'] for lang in data['available_languages']}
        assert available_ids == {1, 2}
        
        # Check availability for movie 2 - should show only Spanish
        response = client.get('/api/movies/2/subtitles/availability')
        data = response.get_json()
        available_ids = {lang['id'] for lang in data['available_languages']}
        assert available_ids == {2}  # Only Spanish

    def test_subtitle_data_integrity_workflow(self, client, sample_data):
        """Test that subtitle data integrity is maintained."""
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # Get subtitles and verify data integrity
        response = client.get('/api/movies/1/subtitles?lang=1')
        data = response.get_json()
        
        lines = data['subtitle_lines']
        
        # Verify all required fields are present
        for line in lines:
            assert 'id' in line
            assert 'sequence' in line
            assert 'content' in line
            assert 'language_id' in line
            assert isinstance(line['id'], int)
            assert isinstance(line['sequence'], int)
            assert isinstance(line['content'], str)
            assert isinstance(line['language_id'], int)
            assert len(line['content'].strip()) > 0
        
        # Verify sequence ordering
        sequences = [line['sequence'] for line in lines]
        assert sequences == sorted(sequences)
        
        # Verify consecutive sequences starting from 1
        assert sequences == list(range(1, len(sequences) + 1))

    def test_cache_invalidation_workflow(self, client, sample_data):
        """Test cache invalidation workflow."""
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # Make initial request to populate cache
        response1 = client.get('/api/movies/1/subtitles?lang=1')
        assert response1.status_code == 200
        
        # Verify item is cached
        cache_response = client.get('/api/subtitles/cache/stats')
        stats = cache_response.get_json()['cache_statistics']
        assert stats['cache_size'] >= 1
        
        # Make another request (should be cache hit)
        response2 = client.get('/api/movies/1/subtitles?lang=1')
        assert response2.status_code == 200
        assert response1.get_json() == response2.get_json()
        
        # Check that we have cache hits
        cache_response = client.get('/api/subtitles/cache/stats')
        stats = cache_response.get_json()['cache_statistics']
        assert stats['hits'] >= 1