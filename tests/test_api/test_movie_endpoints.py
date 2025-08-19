"""Tests for movie API endpoints."""
import pytest
import json
from flask import url_for
from app.models import User


class TestMovieEndpoints:
    """Test cases for movie API endpoints."""

    def test_get_movies_unauthenticated(self, client):
        """Test movies endpoint requires authentication."""
        response = client.get('/api/movies')
        # Flask-Login redirects to login page for unauthenticated requests
        assert response.status_code == 302

    def test_get_movies_missing_language_preferences(self, client, app):
        """Test movies endpoint with user missing language preferences."""
        with app.app_context():
            # Create user without language preferences
            user = User(
                email='no_prefs@example.com',
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            response = client.get('/api/movies')
            assert response.status_code == 400
            
            data = json.loads(response.data)
            assert data['code'] == 'MISSING_LANGUAGE_PREFERENCES'
            assert 'Language preferences not set' in data['error']

    def test_get_movies_with_valid_language_preferences(self, client, app):
        """Test movies endpoint with valid user language preferences."""
        with app.app_context():
            # Create user with language preferences
            user = User(
                email='test_movies@example.com',
                native_language_id=1,  # English
                target_language_id=2,  # Spanish
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                
            # Get movies
            response = client.get('/api/movies')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'movies' in data
            assert 'language_pair' in data
            assert 'total_count' in data
            
            assert data['language_pair']['native_language_id'] == 1
            assert data['language_pair']['target_language_id'] == 2
            assert isinstance(data['movies'], list)
            assert data['total_count'] == len(data['movies'])
            
            # Check movie structure if any movies returned
            if data['movies']:
                movie = data['movies'][0]
                assert 'id' in movie
                assert 'title' in movie

    def test_get_movies_json_response_structure(self, client, app):
        """Test the JSON response structure of movies endpoint."""
        with app.app_context():
            # Create user with language preferences
            user = User(
                email='test_json@example.com',
                native_language_id=1,  # English
                target_language_id=3,  # French
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                
            # Get movies
            response = client.get('/api/movies')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            
            data = json.loads(response.data)
            
            # Verify required keys exist
            required_keys = ['movies', 'language_pair', 'total_count']
            for key in required_keys:
                assert key in data
            
            # Verify language_pair structure
            language_pair = data['language_pair']
            assert 'native_language_id' in language_pair
            assert 'target_language_id' in language_pair

    def test_get_movies_with_no_available_movies(self, client, app):
        """Test movies endpoint when no movies are available for language pair."""
        with app.app_context():
            # Create user with language preferences that might not have movies
            user = User(
                email='test_empty@example.com',
                native_language_id=1,  # English  
                target_language_id=5,  # Italian (might have fewer movies)
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                
            # Get movies
            response = client.get('/api/movies')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert isinstance(data['movies'], list)
            assert data['total_count'] == len(data['movies'])
            # Could be empty or have movies, both are valid responses

    def test_get_movies_with_search_query(self, client, app):
        """Test movies endpoint with search query parameter."""
        with app.app_context():
            # Create user with language preferences
            user = User(
                email='test_search@example.com',
                native_language_id=1,  # English
                target_language_id=2,  # Spanish
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                
            # Search for movies with "Matrix" in the title
            response = client.get('/api/movies?search=Matrix')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'movies' in data
            assert 'search' in data
            assert data['search']['query'] == 'Matrix'
            assert data['search']['result_count'] == len(data['movies'])
            
            # All returned movies should contain "Matrix" in title (case-insensitive)
            for movie in data['movies']:
                assert 'matrix' in movie['title'].lower()

    def test_get_movies_with_empty_search_query(self, client, app):
        """Test movies endpoint with empty search query parameter."""
        with app.app_context():
            # Create user with language preferences
            user = User(
                email='test_empty_search@example.com',
                native_language_id=1,  # English
                target_language_id=2,  # Spanish
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                
            # Search with empty string should be treated as no search
            response = client.get('/api/movies?search=')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'movies' in data
            assert 'search' not in data  # Empty search should not include search metadata

    def test_get_movies_with_no_search_results(self, client, app):
        """Test movies endpoint with search query that returns no results."""
        with app.app_context():
            # Create user with language preferences
            user = User(
                email='test_no_results@example.com',
                native_language_id=1,  # English
                target_language_id=2,  # Spanish
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                
            # Search for non-existent movie
            response = client.get('/api/movies?search=NonExistentMovieTitle12345')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'movies' in data
            assert 'search' in data
            assert data['search']['query'] == 'NonExistentMovieTitle12345'
            assert data['search']['result_count'] == 0
            assert len(data['movies']) == 0

    def test_get_movies_search_case_insensitive(self, client, app):
        """Test that search is case-insensitive."""
        with app.app_context():
            # Create user with language preferences
            user = User(
                email='test_case_insensitive@example.com',
                native_language_id=1,  # English
                target_language_id=2,  # Spanish
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                
            # Search with different cases should return same results
            response1 = client.get('/api/movies?search=matrix')
            response2 = client.get('/api/movies?search=MATRIX')
            response3 = client.get('/api/movies?search=Matrix')
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            assert response3.status_code == 200
            
            data1 = json.loads(response1.data)
            data2 = json.loads(response2.data)
            data3 = json.loads(response3.data)
            
            # All should return the same number of results
            assert len(data1['movies']) == len(data2['movies']) == len(data3['movies'])

    def test_get_movies_search_partial_matching(self, client, app):
        """Test that search supports partial title matching."""
        with app.app_context():
            # Create user with language preferences
            user = User(
                email='test_partial@example.com',
                native_language_id=1,  # English
                target_language_id=2,  # Spanish
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            # Manually set session to simulate logged in user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
                
            # Search for partial word should return matching movies
            response = client.get('/api/movies?search=Mat')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'movies' in data
            assert 'search' in data
            assert data['search']['query'] == 'Mat'
            
            # All returned movies should contain "Mat" somewhere in title
            for movie in data['movies']:
                assert 'mat' in movie['title'].lower()