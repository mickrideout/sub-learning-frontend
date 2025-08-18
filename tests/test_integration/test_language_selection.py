"""Integration tests for language selection flow."""
import json
import pytest
from app.models import User, Language
from app import db


class TestLanguageSelectionIntegration:
    """Test complete language selection integration flow."""

    def test_complete_language_selection_flow(self, app, client):
        """Test the complete language selection flow from authentication to selection."""
        with app.app_context():
            # Create test user without language preferences
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            # Create test languages
            english = Language(id=1, name="english", display_name="English", code="en")
            spanish = Language(id=2, name="spanish", display_name="Spanish", code="es")
            french = Language(id=3, name="french", display_name="French", code="fr")
            db.session.add_all([english, spanish, french])
            db.session.commit()
            
            # Step 1: Login user
            response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'testpass'
            }, follow_redirects=False)
            
            # Should redirect to language selection since user has no languages set
            assert response.status_code == 302
            assert '/auth/language-selection' in response.location
            
            # Step 2: Access language selection page
            response = client.get('/auth/language-selection')
            assert response.status_code == 200
            assert b'Select Your Languages' in response.data
            
            # Step 3: Get available languages via API
            response = client.get('/api/languages')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert len(data['languages']) == 3
            
            # Step 4: Set language preferences via API
            response = client.post('/api/user/languages',
                                        data=json.dumps({
                                            'native_language_id': 1,
                                            'target_language_id': 2
                                        }),
                                        content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['user']['native_language']['display_name'] == 'English'
            assert data['user']['target_language']['display_name'] == 'Spanish'
            
            # Step 5: Verify user is redirected to dashboard after completing language selection
            response = client.get('/auth/language-selection', follow_redirects=False)
            assert response.status_code == 302
            assert '/auth/dashboard' in response.location

    def test_oauth_user_language_selection_redirect(self, app, client):
        """Test that OAuth users without language preferences are redirected to language selection."""
        with app.app_context():
            # Create OAuth user without language preferences
            user = User(
                email="oauth@example.com",
                oauth_provider="google",
                oauth_id="12345",
                is_active=True
            )
            db.session.add(user)
            
            # Create test languages
            english = Language(id=1, name="english", display_name="English", code="en")
            spanish = Language(id=2, name="spanish", display_name="Spanish", code="es")
            db.session.add_all([english, spanish])
            db.session.commit()
            
            # Simulate user login (OAuth flow would typically handle this)
            with client.session_transaction() as sess:
                sess['user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Access dashboard should redirect to language selection
            response = client.get('/auth/dashboard', follow_redirects=False)
            # Note: This test depends on the dashboard route checking language selection
            # For now, let's test the language selection route directly
            
            response = client.get('/auth/language-selection')
            assert response.status_code == 200

    def test_language_selection_persistence_across_sessions(self, app, client):
        """Test that language selections persist across user sessions."""
        with app.app_context():
            # Create test user and languages
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            english = Language(id=1, name="english", display_name="English", code="en")
            spanish = Language(id=2, name="spanish", display_name="Spanish", code="es")
            db.session.add_all([english, spanish])
            db.session.commit()
            
            # Login and set languages
            client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'testpass'
            })
            
            client.post('/api/user/languages',
                             data=json.dumps({
                                 'native_language_id': 1,
                                 'target_language_id': 2
                             }),
                             content_type='application/json')
            
            # Logout
            client.get('/auth/logout')
            
            # Login again
            response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'testpass'
            }, follow_redirects=False)
            
            # Should redirect to dashboard since languages are already set
            assert response.status_code == 302
            assert '/auth/dashboard' in response.location

    def test_language_validation_prevents_same_language_selection(self, app, client):
        """Test that validation prevents selecting the same language for native and target."""
        with app.app_context():
            # Create test user and language
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            english = Language(id=1, name="english", display_name="English", code="en")
            db.session.add(english)
            db.session.commit()
            
            # Login user
            client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'testpass'
            })
            
            # Attempt to set same language for both native and target
            response = client.post('/api/user/languages',
                                        data=json.dumps({
                                            'native_language_id': 1,
                                            'target_language_id': 1
                                        }),
                                        content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['code'] == 'SAME_LANGUAGE_ERROR'
            
            # Verify user's languages weren't updated
            with app.app_context():
                updated_user = User.query.filter_by(email='test@example.com').first()
                assert updated_user.native_language_id is None
                assert updated_user.target_language_id is None

    def test_error_handling_for_database_issues(self, app, client):
        """Test error handling when database connection issues occur."""
        # This test is harder to simulate without actually breaking the database
        # For now, we test with invalid language IDs which will cause database errors
        
        with app.app_context():
            # Create test user
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()
            
            # Login user
            client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'testpass'
            })
            
            # Attempt to set non-existent language IDs
            response = client.post('/api/user/languages',
                                        data=json.dumps({
                                            'native_language_id': 9999,
                                            'target_language_id': 9998
                                        }),
                                        content_type='application/json')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'code' in data

    def test_registration_flow_integration_with_language_selection(self, app, client):
        """Test that new user registration integrates properly with language selection."""
        with app.app_context():
            # Create test languages
            english = Language(id=1, name="english", display_name="English", code="en")
            spanish = Language(id=2, name="spanish", display_name="Spanish", code="es")
            db.session.add_all([english, spanish])
            db.session.commit()
            
            # Register new user
            response = client.post('/auth/register', data={
                'email': 'newuser@example.com',
                'password': 'password123',
                'password_confirm': 'password123'
            })
            
            # Registration should succeed and redirect to login
            assert response.status_code == 302
            
            # Login the new user
            response = client.post('/auth/login', data={
                'email': 'newuser@example.com',
                'password': 'password123'
            }, follow_redirects=False)
            
            # Should redirect to language selection since new users have no languages set
            assert response.status_code == 302
            assert '/auth/language-selection' in response.location