"""Tests for OAuth service layer."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.oauth_service import OAuthService
from app.models.user import User
from app import db


class TestOAuthService:
    """Test suite for OAuth service methods."""

    def test_generate_oauth_state(self):
        """Test OAuth state generation."""
        state1 = OAuthService.generate_oauth_state()
        state2 = OAuthService.generate_oauth_state()
        
        assert len(state1) > 20  # Should be reasonably long
        assert len(state2) > 20
        assert state1 != state2  # Should be unique
        assert isinstance(state1, str)
        assert isinstance(state2, str)

    @patch('app.services.oauth_service.oauth')
    @patch('app.services.oauth_service.session')
    def test_get_authorization_url_google(self, mock_session, mock_oauth, app):
        """Test getting Google OAuth authorization URL."""
        with app.app_context():
            mock_client = Mock()
            mock_client.create_authorization_url.return_value = {'url': 'https://accounts.google.com/oauth/authorize?test=1'}
            mock_oauth.create_client.return_value = mock_client
            
            redirect_uri = 'https://example.com/callback'
            auth_url, state = OAuthService.get_authorization_url('google', redirect_uri)
            
            assert 'https://accounts.google.com' in auth_url
            assert len(state) > 20
            mock_session.__setitem__.assert_any_call('oauth_state', state)
            mock_session.__setitem__.assert_any_call('oauth_provider', 'google')

    @patch('app.services.oauth_service.oauth')
    @patch('app.services.oauth_service.session')
    def test_get_authorization_url_apple(self, mock_session, mock_oauth, app):
        """Test Apple OAuth authorization URL with response_mode=form_post."""
        with app.app_context():
            mock_client = Mock()
            mock_client.create_authorization_url.return_value = {'url': 'https://appleid.apple.com/auth/authorize?test=1'}
            mock_oauth.create_client.return_value = mock_client
            
            redirect_uri = 'https://example.com/callback'
            auth_url, state = OAuthService.get_authorization_url('apple', redirect_uri)
            
            # Apple should call with response_mode=form_post
            mock_client.create_authorization_url.assert_called_with(
                redirect_uri, state=state, response_mode='form_post'
            )

    def test_get_authorization_url_invalid_provider(self):
        """Test getting authorization URL with invalid provider."""
        with pytest.raises(ValueError, match="Unsupported OAuth provider"):
            OAuthService.get_authorization_url('invalid_provider', 'https://example.com/callback')

    def test_validate_state_methods_exist(self):
        """Test that state validation methods exist and are callable."""
        # These methods are tested in integration tests with real Flask context
        assert hasattr(OAuthService, 'validate_state')
        assert callable(OAuthService.validate_state)
        assert hasattr(OAuthService, 'cleanup_oauth_session')
        assert callable(OAuthService.cleanup_oauth_session)

    @patch('app.services.oauth_service.oauth')
    @patch('app.services.oauth_service.current_app')
    def test_get_user_info_google_success(self, mock_app, mock_oauth, app):
        """Test successful Google user info retrieval."""
        with app.app_context():
            mock_client = Mock()
            token = {'access_token': 'test_token', 'id_token': 'test_id_token'}
            mock_client.authorize_access_token.return_value = token
            mock_client.parse_id_token.return_value = {
                'sub': 'google_user_123',
                'email': 'user@example.com',
                'name': 'Test User',
                'given_name': 'Test',
                'family_name': 'User',
                'picture': 'https://example.com/avatar.jpg'
            }
            mock_oauth.create_client.return_value = mock_client
            
            result = OAuthService.get_user_info('google', 'auth_code', 'https://example.com/callback')
            
            assert result['oauth_id'] == 'google_user_123'
            assert result['email'] == 'user@example.com'
            assert result['name'] == 'Test User'

    @patch('app.services.oauth_service.oauth')
    @patch('app.services.oauth_service.current_app')
    def test_get_user_info_facebook_success(self, mock_app, mock_oauth, app):
        """Test successful Facebook user info retrieval."""
        with app.app_context():
            mock_client = Mock()
            token = {'access_token': 'test_token'}
            mock_client.authorize_access_token.return_value = token
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'id': 'facebook_user_456',
                'email': 'user@example.com',
                'name': 'Test User',
                'first_name': 'Test',
                'last_name': 'User',
                'picture': {'data': {'url': 'https://example.com/avatar.jpg'}}
            }
            mock_client.get.return_value = mock_response
            mock_oauth.create_client.return_value = mock_client
            
            result = OAuthService.get_user_info('facebook', 'auth_code', 'https://example.com/callback')
            
            assert result['oauth_id'] == 'facebook_user_456'
            assert result['email'] == 'user@example.com'
            assert result['name'] == 'Test User'

    @patch('app.services.oauth_service.oauth')
    @patch('app.services.oauth_service.current_app')
    def test_get_user_info_no_client(self, mock_app, mock_oauth, app):
        """Test user info retrieval with no OAuth client."""
        with app.app_context():
            mock_oauth.create_client.return_value = None
            
            result = OAuthService.get_user_info('google', 'auth_code', 'https://example.com/callback')
            
            assert result is None

    @patch('app.services.oauth_service.oauth')
    @patch('app.services.oauth_service.current_app')
    def test_get_user_info_token_exchange_failure(self, mock_app, mock_oauth, app):
        """Test user info retrieval when token exchange fails."""
        with app.app_context():
            mock_client = Mock()
            mock_client.authorize_access_token.return_value = None
            mock_oauth.create_client.return_value = mock_client
            
            result = OAuthService.get_user_info('google', 'auth_code', 'https://example.com/callback')
            
            assert result is None

    def test_find_or_create_user_new_user(self, app):
        """Test creating new user from OAuth data."""
        with app.app_context():
            user_info = {
                'oauth_id': 'google_123',
                'email': 'newuser@example.com'
            }
            
            user = OAuthService.find_or_create_user('google', user_info)
            
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.oauth_provider == 'google'
            assert user.oauth_id == 'google_123'
            assert user.email_verified is True

    def test_find_or_create_user_existing_oauth_user(self, app):
        """Test finding existing OAuth user."""
        with app.app_context():
            # Create existing user
            existing_user = User(
                email='existing@example.com',
                oauth_provider='google',
                oauth_id='google_456'
            )
            db.session.add(existing_user)
            db.session.commit()
            existing_id = existing_user.id
            
            user_info = {
                'oauth_id': 'google_456',
                'email': 'existing@example.com'
            }
            
            user = OAuthService.find_or_create_user('google', user_info)
            
            assert user is not None
            assert user.id == existing_id
            assert user.email == 'existing@example.com'

    def test_find_or_create_user_link_to_existing_email_user(self, app):
        """Test linking OAuth to existing email user."""
        with app.app_context():
            # Create existing email user without OAuth
            existing_user = User(email='link@example.com')
            existing_user.set_password('password123')
            db.session.add(existing_user)
            db.session.commit()
            existing_id = existing_user.id
            
            user_info = {
                'oauth_id': 'google_789',
                'email': 'link@example.com'
            }
            
            user = OAuthService.find_or_create_user('google', user_info)
            
            assert user is not None
            assert user.id == existing_id
            assert user.oauth_provider == 'google'
            assert user.oauth_id == 'google_789'

    def test_find_or_create_user_missing_required_data(self, app):
        """Test user creation with missing required data."""
        with app.app_context():
            user_info = {'oauth_id': 'google_123'}  # Missing email
            
            user = OAuthService.find_or_create_user('google', user_info)
            
            assert user is None

    @patch('app.services.oauth_service.login_user')
    @patch('app.services.oauth_service.current_app')
    def test_login_oauth_user_success(self, mock_app, mock_login, app):
        """Test successful OAuth user login."""
        with app.app_context():
            mock_login.return_value = True
            user = User(email='test@example.com')
            
            result = OAuthService.login_oauth_user(user)
            
            assert result is True
            mock_login.assert_called_once_with(user, remember=True)

    @patch('app.services.oauth_service.login_user')
    @patch('app.services.oauth_service.current_app')
    def test_login_oauth_user_failure(self, mock_app, mock_login, app):
        """Test OAuth user login failure."""
        with app.app_context():
            mock_login.side_effect = Exception("Login failed")
            user = User(email='test@example.com')
            
            result = OAuthService.login_oauth_user(user)
            
            assert result is False

