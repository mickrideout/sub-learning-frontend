"""Integration tests for movie catalog functionality."""
import pytest
import json
from flask import url_for
from app.models import User


class TestMovieCatalogIntegration:
    """Integration tests for complete movie catalog flow."""

    def test_complete_movie_catalog_flow(self, client, app):
        """Test the complete flow from login to movie selection."""
        with app.app_context():
            # Create user with language preferences
            user = User(
                email='integration_test@example.com',
                native_language_id=1,  # English
                target_language_id=2,  # Spanish
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            with client:
                # Step 1: Login
                login_response = client.post('/auth/login', data={
                    'email': user.email,
                    'password': 'testpass123'
                })
                assert login_response.status_code == 302  # Redirect after login
                
                # Step 2: Access movie catalog page
                catalog_response = client.get('/movies')
                assert catalog_response.status_code == 200
                assert b'Movie Catalog' in catalog_response.data
                
                # Step 3: Get movies via API
                api_response = client.get('/api/movies')
                assert api_response.status_code == 200
                
                movies_data = json.loads(api_response.data)
                assert 'movies' in movies_data
                assert 'language_pair' in movies_data
                
                # Verify language pair matches user preferences
                language_pair = movies_data['language_pair']
                assert language_pair['native_language_id'] == user.native_language_id
                assert language_pair['target_language_id'] == user.target_language_id

    def test_movie_catalog_without_language_preferences(self, client, app):
        """Test movie catalog flow when user lacks language preferences."""
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
            
            with client:
                # Login
                client.post('/auth/login', data={
                    'email': user.email,
                    'password': 'testpass123'
                })
                
                # Access movie catalog page (should work)
                catalog_response = client.get('/movies')
                assert catalog_response.status_code == 200
                
                # But API should return error
                api_response = client.get('/api/movies')
                assert api_response.status_code == 400
                
                data = json.loads(api_response.data)
                assert data['code'] == 'MISSING_LANGUAGE_PREFERENCES'

    def test_unauthenticated_access_to_movie_catalog(self, client):
        """Test that unauthenticated users can't access movie catalog."""
        # Try to access movie catalog page without login
        response = client.get('/movies')
        assert response.status_code == 302  # Redirect to login
        
        # Try to access API without login
        api_response = client.get('/api/movies')
        assert api_response.status_code == 302  # Redirect to login

    def test_movie_catalog_template_rendering(self, client, app):
        """Test that movie catalog template renders correctly."""
        with app.app_context():
            # Create authenticated user
            user = User(
                email='template_test@example.com',
                native_language_id=1,
                target_language_id=2,
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            with client:
                # Login
                client.post('/auth/login', data={
                    'email': user.email,
                    'password': 'testpass123'
                })
                
                # Get movie catalog page
                response = client.get('/movies')
                assert response.status_code == 200
                
                # Check for key template elements
                content = response.data.decode()
                assert 'Movie Catalog' in content
                assert 'loading-indicator' in content
                assert 'movie-list' in content
                assert 'error-message' in content
                assert 'movieSelectionModal' in content
                assert 'movie-discovery.js' in content

    def test_error_handling_in_movie_catalog(self, client, app):
        """Test error handling in movie catalog when database issues occur."""
        with app.app_context():
            # Create user
            user = User(
                email='error_test@example.com',
                native_language_id=999,  # Invalid language ID
                target_language_id=1000,  # Invalid language ID
                is_active=True
            )
            user.set_password('testpass123')
            
            from app import db
            db.session.add(user)
            db.session.commit()
            
            with client:
                # Login
                client.post('/auth/login', data={
                    'email': user.email,
                    'password': 'testpass123'
                })
                
                # API should handle invalid language IDs gracefully
                api_response = client.get('/api/movies')
                # Should return 500 or handle gracefully
                assert api_response.status_code in [400, 500]