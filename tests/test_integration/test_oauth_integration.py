"""Integration tests for complete OAuth flow."""
import pytest
from unittest.mock import patch, Mock
from app.models.user import User
from app import db
from app.services.oauth_service import OAuthService


class TestOAuthIntegration:
    """Integration tests for complete OAuth authentication flow."""

    def test_complete_google_oauth_flow_new_user(self, app, client):
        """Test complete Google OAuth flow for new user registration."""
        with app.app_context():
            # Step 1: Initiate OAuth flow
            with patch('app.services.oauth_service.oauth') as mock_oauth:
                mock_client = Mock()
                mock_oauth.create_client.return_value = mock_client
                mock_client.create_authorization_url.return_value = {
                    'url': 'https://accounts.google.com/oauth/authorize?client_id=test'
                }
                
                with client.session_transaction() as sess:
                    # Simulate OAuth initiation
                    response = client.get('/auth/oauth/google')
                    assert response.status_code == 302
                    assert 'accounts.google.com' in response.location
                
                # Verify session state was set
                with client.session_transaction() as sess:
                    assert 'oauth_state' in sess
                    assert sess['oauth_provider'] == 'google'
                    stored_state = sess['oauth_state']

            # Step 2: Mock OAuth callback with user creation
            with patch.multiple(
                'app.services.oauth_service',
                oauth=Mock(),
                current_app=Mock()
            ) as mocks:
                # Setup OAuth client mock for token exchange
                mock_client = Mock()
                mock_token = {
                    'access_token': 'test_access_token',
                    'id_token': 'test_id_token'
                }
                mock_client.authorize_access_token.return_value = mock_token
                mock_client.parse_id_token.return_value = {
                    'sub': 'google_user_12345',
                    'email': 'newuser@example.com',
                    'name': 'New User',
                    'given_name': 'New',
                    'family_name': 'User',
                    'picture': 'https://example.com/avatar.jpg'
                }
                mocks['oauth'].create_client.return_value = mock_client
                
                # Simulate successful OAuth callback
                with client.session_transaction() as sess:
                    sess['oauth_state'] = stored_state
                    sess['oauth_provider'] = 'google'
                
                response = client.get(
                    f'/auth/oauth/google/callback?code=test_auth_code&state={stored_state}',
                    follow_redirects=True
                )
                
                assert response.status_code == 200
                assert b'Welcome! You have been logged in via Google' in response.data
                
                # Verify user was created in database
                user = User.query.filter_by(email='newuser@example.com').first()
                assert user is not None
                assert user.oauth_provider == 'google'
                assert user.oauth_id == 'google_user_12345'
                assert user.email_verified is True

    def test_complete_facebook_oauth_flow_existing_user_linking(self, app, client):
        """Test Facebook OAuth flow linking to existing email user."""
        with app.app_context():
            # Create existing user with email/password
            existing_user = User(email='existing@example.com')
            existing_user.set_password('password123')
            db.session.add(existing_user)
            db.session.commit()
            existing_id = existing_user.id
            
            # Step 1: Initiate Facebook OAuth
            with patch('app.services.oauth_service.oauth') as mock_oauth:
                mock_client = Mock()
                mock_oauth.create_client.return_value = mock_client
                mock_client.create_authorization_url.return_value = {
                    'url': 'https://www.facebook.com/v18.0/dialog/oauth?client_id=test'
                }
                
                response = client.get('/auth/oauth/facebook')
                assert response.status_code == 302
                
                with client.session_transaction() as sess:
                    stored_state = sess['oauth_state']

            # Step 2: Complete OAuth callback with account linking
            with patch.multiple(
                'app.services.oauth_service',
                oauth=Mock(),
                current_app=Mock()
            ) as mocks:
                mock_client = Mock()
                mock_token = {'access_token': 'fb_access_token'}
                mock_client.authorize_access_token.return_value = mock_token
                
                # Mock Facebook API response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'id': 'facebook_user_67890',
                    'email': 'existing@example.com',
                    'name': 'Existing User',
                    'first_name': 'Existing',
                    'last_name': 'User',
                    'picture': {'data': {'url': 'https://example.com/fb_avatar.jpg'}}
                }
                mock_client.get.return_value = mock_response
                mocks['oauth'].create_client.return_value = mock_client
                
                with client.session_transaction() as sess:
                    sess['oauth_state'] = stored_state
                    sess['oauth_provider'] = 'facebook'
                
                response = client.get(
                    f'/auth/oauth/facebook/callback?code=fb_auth_code&state={stored_state}',
                    follow_redirects=True
                )
                
                assert response.status_code == 200
                assert b'Welcome! You have been logged in via Facebook' in response.data
                
                # Verify existing user was linked to Facebook OAuth
                user = User.query.get(existing_id)
                assert user.oauth_provider == 'facebook'
                assert user.oauth_id == 'facebook_user_67890'
                assert user.email == 'existing@example.com'

    def test_oauth_csrf_protection(self, app, client):
        """Test OAuth CSRF protection with state parameter validation."""
        with app.app_context():
            # Attempt OAuth callback with invalid state
            response = client.get(
                '/auth/oauth/google/callback?code=test_code&state=invalid_state',
                follow_redirects=True
            )
            
            assert response.status_code == 200
            assert b'OAuth security validation failed' in response.data
            
            # Verify no user was created or logged in
            assert User.query.count() == 0

    def test_oauth_error_handling_provider_rejection(self, client):
        """Test OAuth error handling when provider rejects authorization."""
        response = client.get(
            '/auth/oauth/google/callback?error=access_denied&error_description=User%20denied%20access',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'OAuth login cancelled or failed' in response.data
        assert b'User denied access' in response.data

    def test_oauth_session_cleanup(self, app, client):
        """Test OAuth session data is properly cleaned up."""
        with app.app_context():
            # Initiate OAuth to set session data
            with patch('app.services.oauth_service.oauth') as mock_oauth:
                mock_client = Mock()
                mock_oauth.create_client.return_value = mock_client
                mock_client.create_authorization_url.return_value = {
                    'url': 'https://accounts.google.com/oauth/authorize'
                }
                
                client.get('/auth/oauth/google')
                
                # Verify session data is set
                with client.session_transaction() as sess:
                    assert 'oauth_state' in sess
                    assert 'oauth_provider' in sess

            # Complete OAuth callback (with failure to trigger cleanup)
            response = client.get(
                '/auth/oauth/google/callback?error=access_denied',
                follow_redirects=True
            )
            
            # Verify session data is cleaned up
            with client.session_transaction() as sess:
                assert 'oauth_state' not in sess
                assert 'oauth_provider' not in sess

    def test_oauth_duplicate_provider_prevention(self, app, client):
        """Test prevention of duplicate OAuth accounts for same provider."""
        with app.app_context():
            # Create user with existing OAuth provider
            existing_user = User(
                email='user@example.com',
                oauth_provider='google',
                oauth_id='google_existing_123'
            )
            db.session.add(existing_user)
            db.session.commit()
            
            # Attempt to link same email to different OAuth account on same provider
            user_info = {
                'oauth_id': 'google_different_456',
                'email': 'user@example.com'
            }
            
            # This should find and return the existing user, not create new
            found_user = OAuthService.find_or_create_user('google', user_info)
            assert found_user.id == existing_user.id
            assert found_user.oauth_id == 'google_existing_123'  # Original ID preserved

    def test_oauth_provider_specific_flows(self, app, client):
        """Test provider-specific OAuth configuration differences."""
        with app.app_context():
            # Test Apple Sign-In specific configuration
            with patch('app.services.oauth_service.oauth') as mock_oauth:
                mock_client = Mock()
                mock_oauth.create_client.return_value = mock_client
                mock_client.create_authorization_url.return_value = {
                    'url': 'https://appleid.apple.com/auth/authorize'
                }
                
                redirect_uri = 'https://example.com/callback'
                auth_url, state = OAuthService.get_authorization_url('apple', redirect_uri)
                
                # Verify Apple-specific response_mode=form_post was used
                mock_client.create_authorization_url.assert_called_with(
                    redirect_uri, state=state, response_mode='form_post'
                )

    def test_oauth_token_secure_storage(self, app, client):
        """Test OAuth tokens are securely handled and not exposed."""
        with app.app_context():
            with patch.multiple(
                'app.services.oauth_service',
                oauth=Mock(),
                current_app=Mock()
            ) as mocks:
                # Setup mock for successful token exchange
                mock_client = Mock()
                mock_token = {
                    'access_token': 'sensitive_access_token',
                    'refresh_token': 'sensitive_refresh_token',
                    'id_token': 'id_token_with_user_info'
                }
                mock_client.authorize_access_token.return_value = mock_token
                mock_client.parse_id_token.return_value = {
                    'sub': 'user_123',
                    'email': 'secure@example.com'
                }
                mocks['oauth'].create_client.return_value = mock_client
                
                # Test token handling doesn't store sensitive data in user model
                user_info = OAuthService.get_user_info('google', 'auth_code', 'callback_uri')
                
                assert 'access_token' not in user_info
                assert 'refresh_token' not in user_info
                assert user_info['oauth_id'] == 'user_123'
                assert user_info['email'] == 'secure@example.com'

    def test_oauth_profile_display_integration(self, app, client):
        """Test OAuth authentication method display in user profile."""
        with app.app_context():
            # Create OAuth user
            oauth_user = User(
                email='oauth@example.com',
                oauth_provider='google',
                oauth_id='google_profile_123',
                email_verified=True
            )
            db.session.add(oauth_user)
            db.session.commit()
            
            # Login user and check profile display
            with client.session_transaction() as sess:
                sess['_user_id'] = str(oauth_user.id)
                sess['_fresh'] = True
            
            response = client.get('/auth/profile')
            assert response.status_code == 200
            assert b'Google OAuth' in response.data
            assert b'fa-google' in response.data  # Font Awesome icon
            assert b'Verified' in response.data  # Email verified status

    def test_oauth_api_endpoint_integration(self, app, client):
        """Test OAuth API endpoints for AJAX integration."""
        with app.app_context():
            with patch('app.services.oauth_service.oauth') as mock_oauth:
                mock_client = Mock()
                mock_oauth.create_client.return_value = mock_client
                mock_client.create_authorization_url.return_value = {
                    'url': 'https://accounts.google.com/oauth/authorize?test=1'
                }
                
                # Test API OAuth endpoint
                response = client.get('/auth/api/oauth/google')
                assert response.status_code == 200
                
                data = response.get_json()
                assert 'authorization_url' in data
                assert 'state' in data
                assert 'accounts.google.com' in data['authorization_url']