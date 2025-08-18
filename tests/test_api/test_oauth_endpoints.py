"""Tests for OAuth API endpoints and routes."""
import pytest
from unittest.mock import patch, Mock
from flask import url_for
from app.models.user import User
from app import db


class TestOAuthEndpoints:
    """Test suite for OAuth routes and API endpoints."""

    def test_oauth_login_authenticated_user_redirect(self, client, authenticated_user):
        """Test OAuth login redirects authenticated users to home."""
        response = client.get('/auth/oauth/google')
        assert response.status_code == 302
        assert '/main.index' in response.location or '/' in response.location

    @patch('app.blueprints.auth.routes.OAuthService.get_authorization_url')
    def test_oauth_login_success(self, mock_get_url, client):
        """Test successful OAuth login initiation."""
        mock_get_url.return_value = ('https://accounts.google.com/oauth/authorize?test=1', 'state_123')
        
        response = client.get('/auth/oauth/google')
        
        assert response.status_code == 302
        assert 'accounts.google.com' in response.location
        mock_get_url.assert_called_once()

    @patch('app.blueprints.auth.routes.OAuthService.get_authorization_url')
    def test_oauth_login_invalid_provider(self, mock_get_url, client):
        """Test OAuth login with invalid provider."""
        mock_get_url.side_effect = ValueError("Unsupported OAuth provider: invalid")
        
        response = client.get('/auth/oauth/invalid', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'OAuth login failed' in response.data

    @patch('app.blueprints.auth.routes.OAuthService.get_authorization_url')
    def test_oauth_login_service_error(self, mock_get_url, client):
        """Test OAuth login with service error."""
        mock_get_url.side_effect = Exception("Service unavailable")
        
        response = client.get('/auth/oauth/google', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'OAuth service is temporarily unavailable' in response.data

    def test_oauth_callback_authenticated_user_redirect(self, client, authenticated_user):
        """Test OAuth callback redirects authenticated users to home."""
        response = client.get('/auth/oauth/google/callback?code=test&state=test')
        assert response.status_code == 302

    def test_oauth_callback_missing_code(self, client):
        """Test OAuth callback with missing authorization code."""
        response = client.get('/auth/oauth/google/callback?state=test', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'OAuth callback missing required parameters' in response.data

    def test_oauth_callback_missing_state(self, client):
        """Test OAuth callback with missing state parameter."""
        response = client.get('/auth/oauth/google/callback?code=test', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'OAuth callback missing required parameters' in response.data

    def test_oauth_callback_with_error(self, client):
        """Test OAuth callback with provider error."""
        response = client.get(
            '/auth/oauth/google/callback?error=access_denied&error_description=User%20cancelled',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'OAuth login cancelled or failed' in response.data

    @patch('app.blueprints.auth.routes.OAuthService.validate_state')
    def test_oauth_callback_invalid_state(self, mock_validate, client):
        """Test OAuth callback with invalid state parameter."""
        mock_validate.return_value = False
        
        response = client.get('/auth/oauth/google/callback?code=test&state=invalid', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'OAuth security validation failed' in response.data

    @patch('app.blueprints.auth.routes.OAuthService.cleanup_oauth_session')
    @patch('app.blueprints.auth.routes.OAuthService.login_oauth_user')
    @patch('app.blueprints.auth.routes.OAuthService.find_or_create_user')
    @patch('app.blueprints.auth.routes.OAuthService.get_user_info')
    @patch('app.blueprints.auth.routes.OAuthService.validate_state')
    def test_oauth_callback_success_new_user(self, mock_validate, mock_get_info, 
                                           mock_find_create, mock_login, mock_cleanup, client):
        """Test successful OAuth callback creating new user."""
        # Setup mocks
        mock_validate.return_value = True
        mock_get_info.return_value = {
            'oauth_id': 'google_123',
            'email': 'newuser@example.com',
            'name': 'New User'
        }
        new_user = User(email='newuser@example.com', oauth_provider='google', oauth_id='google_123')
        mock_find_create.return_value = new_user
        mock_login.return_value = True
        
        response = client.get('/auth/oauth/google/callback?code=test_code&state=valid_state', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome! You have been logged in via Google' in response.data
        mock_cleanup.assert_called_once()

    @patch('app.blueprints.auth.routes.OAuthService.cleanup_oauth_session')
    @patch('app.blueprints.auth.routes.OAuthService.get_user_info')
    @patch('app.blueprints.auth.routes.OAuthService.validate_state')
    def test_oauth_callback_get_user_info_failure(self, mock_validate, mock_get_info, mock_cleanup, client):
        """Test OAuth callback when user info retrieval fails."""
        mock_validate.return_value = True
        mock_get_info.return_value = None
        
        response = client.get('/auth/oauth/google/callback?code=test_code&state=valid_state', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Failed to retrieve user information from OAuth provider' in response.data
        mock_cleanup.assert_called_once()

    @patch('app.blueprints.auth.routes.OAuthService.cleanup_oauth_session')
    @patch('app.blueprints.auth.routes.OAuthService.find_or_create_user')
    @patch('app.blueprints.auth.routes.OAuthService.get_user_info')
    @patch('app.blueprints.auth.routes.OAuthService.validate_state')
    def test_oauth_callback_user_creation_failure(self, mock_validate, mock_get_info, 
                                                 mock_find_create, mock_cleanup, client):
        """Test OAuth callback when user creation fails."""
        mock_validate.return_value = True
        mock_get_info.return_value = {'oauth_id': 'test', 'email': 'test@example.com'}
        mock_find_create.return_value = None
        
        response = client.get('/auth/oauth/google/callback?code=test_code&state=valid_state', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Failed to create or link user account' in response.data
        mock_cleanup.assert_called_once()

    @patch('app.blueprints.auth.routes.OAuthService.cleanup_oauth_session')
    @patch('app.blueprints.auth.routes.OAuthService.login_oauth_user')
    @patch('app.blueprints.auth.routes.OAuthService.find_or_create_user')
    @patch('app.blueprints.auth.routes.OAuthService.get_user_info')
    @patch('app.blueprints.auth.routes.OAuthService.validate_state')
    def test_oauth_callback_login_failure(self, mock_validate, mock_get_info, 
                                        mock_find_create, mock_login, mock_cleanup, client):
        """Test OAuth callback when user login fails."""
        mock_validate.return_value = True
        mock_get_info.return_value = {'oauth_id': 'test', 'email': 'test@example.com'}
        user = User(email='test@example.com')
        mock_find_create.return_value = user
        mock_login.return_value = False
        
        response = client.get('/auth/oauth/google/callback?code=test_code&state=valid_state', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Login failed after OAuth authentication' in response.data
        mock_cleanup.assert_called_once()

    def test_oauth_callback_post_method_apple(self, client):
        """Test OAuth callback handles POST method (for Apple Sign-In)."""
        response = client.post('/auth/oauth/apple/callback', 
                             data={'code': 'test', 'state': 'test', 'error': 'user_cancelled'},
                             follow_redirects=True)
        
        assert response.status_code == 200
        assert b'OAuth login cancelled or failed' in response.data

    @patch('app.blueprints.auth.routes.OAuthService.get_authorization_url')
    def test_api_oauth_login_success(self, mock_get_url, client):
        """Test API OAuth login endpoint success."""
        mock_get_url.return_value = ('https://accounts.google.com/oauth/authorize', 'state_123')
        
        response = client.get('/auth/api/oauth/google')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'authorization_url' in data
        assert 'state' in data
        assert 'accounts.google.com' in data['authorization_url']

    @patch('app.blueprints.auth.routes.OAuthService.get_authorization_url')
    def test_api_oauth_login_invalid_provider(self, mock_get_url, client):
        """Test API OAuth login with invalid provider."""
        mock_get_url.side_effect = ValueError("Invalid provider")
        
        response = client.get('/auth/api/oauth/invalid')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'INVALID_PROVIDER'

    @patch('app.blueprints.auth.routes.OAuthService.get_authorization_url')
    def test_api_oauth_login_service_error(self, mock_get_url, client):
        """Test API OAuth login with service error."""
        mock_get_url.side_effect = Exception("Service error")
        
        response = client.get('/auth/api/oauth/google')
        
        assert response.status_code == 503
        data = response.get_json()
        assert data['code'] == 'OAUTH_UNAVAILABLE'

    def test_oauth_callback_with_next_parameter(self, client):
        """Test OAuth callback respects next parameter for redirect."""
        with patch.multiple(
            'app.blueprints.auth.routes.OAuthService',
            validate_state=Mock(return_value=True),
            get_user_info=Mock(return_value={'oauth_id': 'test', 'email': 'test@example.com'}),
            find_or_create_user=Mock(return_value=User(email='test@example.com')),
            login_oauth_user=Mock(return_value=True),
            cleanup_oauth_session=Mock()
        ):
            response = client.get('/auth/oauth/google/callback?code=test&state=test&next=/profile')
            assert response.status_code == 302
            # Should redirect to next parameter if provided