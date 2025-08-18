"""Authentication service tests."""
import pytest
from unittest.mock import patch
from app.models import User
from app.services.auth_service import AuthService, AuthenticationError


class TestAuthServiceDetailed:
    """Detailed tests for AuthService methods."""
    
    def test_register_user_email_normalization(self, app, db):
        """Test email normalization during registration."""
        with app.app_context():
            user = AuthService.register_user('  Test@Example.COM  ', 'TestPassword123')
            
            assert user.email == 'test@example.com'  # Should be lowercase and stripped
    
    def test_register_user_with_language_preferences(self, app, db):
        """Test user registration with language preferences."""
        with app.app_context():
            user = AuthService.register_user(
                'test@example.com',
                'TestPassword123',
                native_language_id=1,
                target_language_id=2
            )
            
            assert user.native_language_id == 1
            assert user.target_language_id == 2
    
    def test_register_user_database_rollback_on_error(self, app, db):
        """Test database rollback when registration fails."""
        with app.app_context():
            # Mock db.session.commit to raise an exception
            with patch('app.services.auth_service.db.session.commit', side_effect=Exception('Database error')):
                with pytest.raises(AuthenticationError, match='Registration failed'):
                    AuthService.register_user('test@example.com', 'TestPassword123')
                
                # Verify user was not created
                user = User.query.filter_by(email='test@example.com').first()
                assert user is None
    
    def test_authenticate_user_email_normalization(self, app, db):
        """Test email normalization during authentication."""
        with app.app_context():
            # Register with mixed case
            registered_user = AuthService.register_user('Test@Example.COM', 'TestPassword123')
            
            # Authenticate with different case and whitespace
            authenticated_user = AuthService.authenticate_user('  test@example.com  ', 'TestPassword123')
            
            assert authenticated_user.id == registered_user.id
    
    def test_authenticate_user_logs_attempts(self, app, db):
        """Test that authentication attempts are logged."""
        with app.app_context():
            # Create user
            AuthService.register_user('test@example.com', 'TestPassword123')
            
            with patch('app.services.auth_service.current_app.logger') as mock_logger:
                # Successful authentication
                AuthService.authenticate_user('test@example.com', 'TestPassword123')
                mock_logger.info.assert_called_with('Successful login for user: test@example.com')
                
                # Failed authentication
                with pytest.raises(AuthenticationError):
                    AuthService.authenticate_user('test@example.com', 'WrongPassword')
                mock_logger.warning.assert_called_with('Failed login attempt for user: test@example.com')
    
    def test_reset_password_database_rollback_on_error(self, app, db):
        """Test database rollback when password reset fails."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
            
            # Mock db.session.commit to raise an exception
            with patch('app.services.auth_service.db.session.commit', side_effect=Exception('Database error')):
                with pytest.raises(AuthenticationError, match='Password reset failed'):
                    AuthService.reset_password('test@example.com', 'NewPassword123')
                
                # Verify password wasn't changed
                db.session.refresh(user)
                assert user.check_password('TestPassword123')  # Old password still works
                assert not user.check_password('NewPassword123')  # New password doesn't work
    
    def test_reset_password_updates_timestamp(self, app, db):
        """Test that password reset updates the user's updated_at timestamp."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
            original_updated_at = user.updated_at
            
            # Wait a moment to ensure timestamp difference
            import time
            time.sleep(0.1)
            
            # Reset password
            AuthService.reset_password('test@example.com', 'NewPassword123')
            
            # Verify timestamp was updated
            db.session.refresh(user)
            assert user.updated_at > original_updated_at
    
    def test_deactivate_user_updates_timestamp(self, app, db):
        """Test that user deactivation updates the updated_at timestamp."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
            original_updated_at = user.updated_at
            
            # Wait a moment to ensure timestamp difference
            import time
            time.sleep(0.1)
            
            # Deactivate user
            AuthService.deactivate_user(user.id)
            
            # Verify timestamp was updated
            db.session.refresh(user)
            assert user.updated_at > original_updated_at
            assert user.is_active is False
    
    def test_deactivate_user_database_rollback_on_error(self, app, db):
        """Test database rollback when user deactivation fails."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
            
            # Mock db.session.commit to raise an exception
            with patch('app.services.auth_service.db.session.commit', side_effect=Exception('Database error')):
                with pytest.raises(AuthenticationError, match='User deactivation failed'):
                    AuthService.deactivate_user(user.id)
                
                # Verify user is still active
                db.session.refresh(user)
                assert user.is_active is True
    
    def test_password_reset_token_generation_uniqueness(self, app):
        """Test that password reset tokens are unique."""
        with app.app_context():
            tokens = set()
            for _ in range(100):  # Generate 100 tokens
                token = AuthService.generate_password_reset_token()
                tokens.add(token)
            
            # All tokens should be unique
            assert len(tokens) == 100
    
    def test_password_reset_token_validation_edge_cases(self, app):
        """Test password reset token validation edge cases."""
        with app.app_context():
            # Test various invalid inputs
            invalid_tokens = [
                None,
                '',
                'short',
                'a' * 31,  # Just under minimum length
                123,  # Not a string
                [],  # Wrong type
                {}   # Wrong type
            ]
            
            for invalid_token in invalid_tokens:
                assert AuthService.validate_password_reset_token(invalid_token) is False
    
    def test_service_error_handling_logging(self, app, db):
        """Test that service errors are properly logged."""
        with app.app_context():
            with patch('app.services.auth_service.current_app.logger') as mock_logger:
                # Test registration logging
                AuthService.register_user('test@example.com', 'TestPassword123')
                mock_logger.info.assert_called_with('New user registered: test@example.com')
                
                # Test password reset logging
                AuthService.reset_password('test@example.com', 'NewPassword123')
                mock_logger.info.assert_called_with('Password reset successful for user: test@example.com')
                
                # Test deactivation logging
                user = User.query.filter_by(email='test@example.com').first()
                AuthService.deactivate_user(user.id)
                mock_logger.info.assert_called_with('User deactivated: test@example.com')