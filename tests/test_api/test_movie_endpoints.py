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