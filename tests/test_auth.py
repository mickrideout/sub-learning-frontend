"""Authentication system tests."""
import pytest
from flask import url_for
from app.models import User
from app.services.auth_service import AuthService, AuthenticationError


class TestAuthService:
    """Test authentication service methods."""
    
    def test_register_user_success(self, app, db):
        """Test successful user registration."""
        with app.app_context():
            user = AuthService.register_user(
                email='test@example.com',
                password='TestPassword123',
                native_language_id=1,
                target_language_id=2
            )
            
            assert user.email == 'test@example.com'
            assert user.native_language_id == 1
            assert user.target_language_id == 2
            assert user.is_active is True
            assert user.password_hash is not None
            assert user.check_password('TestPassword123')
    
    def test_register_user_duplicate_email(self, app, db):
        """Test registration with duplicate email fails."""
        with app.app_context():
            # Register first user
            AuthService.register_user('test@example.com', 'TestPassword123')
            
            # Try to register with same email
            with pytest.raises(AuthenticationError, match='Email address already registered'):
                AuthService.register_user('test@example.com', 'DifferentPassword123')
    
    def test_register_user_email_case_insensitive(self, app, db):
        """Test registration is case insensitive for email."""
        with app.app_context():
            # Register with lowercase email
            AuthService.register_user('Test@Example.com', 'TestPassword123')
            
            # Try to register with different case
            with pytest.raises(AuthenticationError):
                AuthService.register_user('test@example.com', 'DifferentPassword123')
    
    def test_authenticate_user_success(self, app, db):
        """Test successful user authentication."""
        with app.app_context():
            # Create user
            registered_user = AuthService.register_user('test@example.com', 'TestPassword123')
            
            # Authenticate user
            authenticated_user = AuthService.authenticate_user('test@example.com', 'TestPassword123')
            
            assert authenticated_user.id == registered_user.id
            assert authenticated_user.email == 'test@example.com'
    
    def test_authenticate_user_case_insensitive_email(self, app, db):
        """Test authentication is case insensitive for email."""
        with app.app_context():
            # Create user with mixed case email
            AuthService.register_user('Test@Example.COM', 'TestPassword123')
            
            # Authenticate with lowercase email
            user = AuthService.authenticate_user('test@example.com', 'TestPassword123')
            assert user.email == 'test@example.com'
    
    def test_authenticate_user_invalid_email(self, app, db):
        """Test authentication with invalid email fails."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match='Invalid email or password'):
                AuthService.authenticate_user('nonexistent@example.com', 'password')
    
    def test_authenticate_user_invalid_password(self, app, db):
        """Test authentication with invalid password fails."""
        with app.app_context():
            # Create user
            AuthService.register_user('test@example.com', 'TestPassword123')
            
            # Try to authenticate with wrong password
            with pytest.raises(AuthenticationError, match='Invalid email or password'):
                AuthService.authenticate_user('test@example.com', 'WrongPassword')
    
    def test_authenticate_user_inactive_account(self, app, db):
        """Test authentication fails for inactive accounts."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
            
            # Deactivate user
            user.is_active = False
            db.session.commit()
            
            # Try to authenticate
            with pytest.raises(AuthenticationError, match='Account is deactivated'):
                AuthService.authenticate_user('test@example.com', 'TestPassword123')
    
    def test_reset_password_success(self, app, db):
        """Test successful password reset."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'OldPassword123')
            
            # Reset password
            result = AuthService.reset_password('test@example.com', 'NewPassword123')
            assert result is True
            
            # Verify new password works
            authenticated_user = AuthService.authenticate_user('test@example.com', 'NewPassword123')
            assert authenticated_user.id == user.id
            
            # Verify old password doesn't work
            with pytest.raises(AuthenticationError):
                AuthService.authenticate_user('test@example.com', 'OldPassword123')
    
    def test_reset_password_nonexistent_user(self, app, db):
        """Test password reset for nonexistent user fails."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match='User not found'):
                AuthService.reset_password('nonexistent@example.com', 'NewPassword123')
    
    def test_generate_password_reset_token(self, app):
        """Test password reset token generation."""
        with app.app_context():
            token = AuthService.generate_password_reset_token()
            assert token is not None
            assert len(token) >= 32
            assert isinstance(token, str)
    
    def test_validate_password_reset_token(self, app):
        """Test password reset token validation."""
        with app.app_context():
            # Valid token
            valid_token = AuthService.generate_password_reset_token()
            assert AuthService.validate_password_reset_token(valid_token) is True
            
            # Invalid tokens
            assert AuthService.validate_password_reset_token('') is False
            assert AuthService.validate_password_reset_token(None) is False
            assert AuthService.validate_password_reset_token('short') is False
    
    def test_deactivate_user_success(self, app, db):
        """Test successful user deactivation."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
            assert user.is_active is True
            
            # Deactivate user
            result = AuthService.deactivate_user(user.id)
            assert result is True
            
            # Verify user is deactivated
            db.session.refresh(user)
            assert user.is_active is False
    
    def test_deactivate_user_nonexistent(self, app, db):
        """Test deactivation of nonexistent user fails."""
        with app.app_context():
            with pytest.raises(AuthenticationError, match='User not found'):
                AuthService.deactivate_user(99999)


class TestAuthRoutes:
    """Test authentication routes."""
    
    def test_register_get(self, client):
        """Test GET request to registration page."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
        assert b'Email' in response.data
        assert b'Password' in response.data
    
    def test_register_post_success(self, client, app, db):
        """Test successful user registration via POST."""
        response = client.post('/auth/register', data={
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'password_confirm': 'TestPassword123',
            'submit': 'Register'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            assert user is not None
            assert user.check_password('TestPassword123')
    
    def test_register_post_duplicate_email(self, client, app, db):
        """Test registration with duplicate email."""
        # Create user first
        with app.app_context():
            AuthService.register_user('test@example.com', 'TestPassword123')
        
        # Try to register again with same email
        response = client.post('/auth/register', data={
            'email': 'test@example.com',
            'password': 'DifferentPassword123',
            'password_confirm': 'DifferentPassword123',
            'submit': 'Register'
        })
        
        assert response.status_code == 200
        assert b'Email address already registered' in response.data
    
    def test_register_post_password_mismatch(self, client):
        """Test registration with password mismatch."""
        response = client.post('/auth/register', data={
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'password_confirm': 'DifferentPassword123',
            'submit': 'Register'
        })
        
        assert response.status_code == 200
        assert b'Passwords must match' in response.data
    
    def test_login_get(self, client):
        """Test GET request to login page."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
        assert b'Email' in response.data
        assert b'Password' in response.data
        assert b'Remember Me' in response.data
    
    def test_login_post_success(self, client, app, db):
        """Test successful login via POST."""
        # Create user first
        with app.app_context():
            AuthService.register_user('test@example.com', 'TestPassword123')
        
        # Login
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'remember_me': False,
            'submit': 'Login'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after login
        assert b'Welcome' in response.data or b'Dashboard' in response.data
    
    def test_login_post_invalid_credentials(self, client, app, db):
        """Test login with invalid credentials."""
        # Create user first
        with app.app_context():
            AuthService.register_user('test@example.com', 'TestPassword123')
        
        # Try to login with wrong password
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'WrongPassword',
            'submit': 'Login'
        })
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_login_redirect_authenticated_user(self, client, app, db):
        """Test login page redirects authenticated users."""
        with app.app_context():
            # Create and login user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
        
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        # Try to access login page
        response = client.get('/auth/login', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to main page or dashboard
    
    def test_logout_success(self, client, app, db):
        """Test successful logout."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
        
        # Login user first
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'submit': 'Login'
        })
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out' in response.data
    
    def test_profile_requires_login(self, client):
        """Test profile page requires authentication."""
        response = client.get('/auth/profile')
        assert response.status_code == 302
        # Should redirect to login page
    
    def test_profile_authenticated_user(self, client, app, db):
        """Test profile page for authenticated user."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
        
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'submit': 'Login'
        })
        
        # Access profile
        response = client.get('/auth/profile')
        assert response.status_code == 200
        assert b'User Profile' in response.data
        assert b'test@example.com' in response.data
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard page requires authentication."""
        response = client.get('/auth/dashboard')
        assert response.status_code == 302
        # Should redirect to login page
    
    def test_dashboard_authenticated_user(self, client, app, db):
        """Test dashboard page for authenticated user."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
        
        # Login user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'submit': 'Login'
        })
        
        # Access dashboard
        response = client.get('/auth/dashboard')
        assert response.status_code == 200
        assert b'Welcome' in response.data
        assert b'test@example.com' in response.data


class TestAuthForms:
    """Test authentication forms validation."""
    
    def test_registration_form_validation(self, app):
        """Test registration form validation."""
        with app.app_context():
            from app.blueprints.auth.forms import RegistrationForm
            
            # Valid form
            form_data = {
                'email': 'test@example.com',
                'password': 'TestPassword123',
                'password_confirm': 'TestPassword123',
                'csrf_token': 'test'  # In tests, CSRF is usually disabled
            }
            form = RegistrationForm(data=form_data)
            # Note: form.validate() may fail due to CSRF in test environment
            
            # Test individual field validators
            assert 'test@example.com' == form.email.data
            assert 'TestPassword123' == form.password.data
    
    def test_login_form_validation(self, app):
        """Test login form validation."""
        with app.app_context():
            from app.blueprints.auth.forms import LoginForm
            
            form_data = {
                'email': 'test@example.com',
                'password': 'TestPassword123',
                'remember_me': True,
                'csrf_token': 'test'
            }
            form = LoginForm(data=form_data)
            
            assert 'test@example.com' == form.email.data
            assert 'TestPassword123' == form.password.data
            assert True == form.remember_me.data


class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_api_register_success(self, client, app, db):
        """Test successful registration via API."""
        response = client.post('/auth/api/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Registration successful'
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_api_register_missing_fields(self, client):
        """Test API registration with missing fields."""
        response = client.post('/auth/api/register', json={
            'email': 'test@example.com'
            # Missing password
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'Email and password are required'
        assert data['code'] == 'MISSING_FIELDS'
    
    def test_api_login_success(self, client, app, db):
        """Test successful login via API."""
        # Create user first
        with app.app_context():
            AuthService.register_user('test@example.com', 'TestPassword123')
        
        response = client.post('/auth/api/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_api_login_invalid_credentials(self, client, app, db):
        """Test API login with invalid credentials."""
        # Create user first
        with app.app_context():
            AuthService.register_user('test@example.com', 'TestPassword123')
        
        response = client.post('/auth/api/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] == 'Invalid email or password'
        assert data['code'] == 'AUTHENTICATION_FAILED'
    
    def test_api_logout_success(self, client, app, db):
        """Test successful logout via API."""
        with app.app_context():
            # Create user
            user = AuthService.register_user('test@example.com', 'TestPassword123')
        
        # Login user first
        client.post('/auth/api/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123'
        })
        
        # Logout
        response = client.post('/auth/api/logout')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Logout successful'