"""Tests for language API endpoints."""
import json
import pytest
from flask_login import login_user
from app.models import User, Language
from app import db


class TestLanguageEndpoints:
    """Test language-related API endpoints."""

    def test_get_languages_success(self, app, client):
        """Test successful retrieval of all languages."""
        with app.app_context():
            # Create test languages
            languages = [
                Language(id=1, name="english", display_name="English", code="en"),
                Language(id=2, name="spanish", display_name="Spanish", code="es"),
                Language(id=3, name="french", display_name="French", code="fr")
            ]
            db.session.add_all(languages)
            db.session.commit()
            
        # Test the API endpoint
        response = client.get('/api/languages')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'languages' in data
        assert len(data['languages']) == 3
        
        # Check that languages are sorted alphabetically by display_name
        display_names = [lang['display_name'] for lang in data['languages']]
        assert display_names == ['English', 'French', 'Spanish']
        
        # Verify language structure
        first_lang = data['languages'][0]
        assert 'id' in first_lang
        assert 'name' in first_lang
        assert 'display_name' in first_lang
        assert 'code' in first_lang

    def test_get_languages_empty_database(self, app, client):
        """Test language API with no languages in database."""
        with app.app_context():
            # Ensure languages table is empty
            Language.query.delete()
            db.session.commit()
            
        response = client.get('/api/languages')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'languages' in data
        assert data['languages'] == []

    def test_update_user_languages_success(self, app, client):
        """Test successful user language update."""
        with app.app_context():
            # Create test user
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            # Create test languages
            english = Language(id=1, name="english", display_name="English", code="en")
            spanish = Language(id=2, name="spanish", display_name="Spanish", code="es")
            db.session.add_all([english, spanish])
            db.session.commit()
            
            # Login the user for the request context
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
        
        # Test the API endpoint
        response = client.post('/api/user/languages',
                                    data=json.dumps({
                                        'native_language_id': 1,
                                        'target_language_id': 2
                                    }),
                                    content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'message' in data
        assert 'user' in data
        assert data['user']['native_language']['id'] == 1
        assert data['user']['target_language']['id'] == 2

    def test_update_user_languages_same_language_error(self, app, client):
        """Test language update with same native and target language."""
        with app.app_context():
            # Create test user and language
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            english = Language(id=1, name="english", display_name="English", code="en")
            db.session.add(english)
            db.session.commit()
            
            # Login the user for the request context
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
        
        # Test the API endpoint with same language
        response = client.post('/api/user/languages',
                                    data=json.dumps({
                                        'native_language_id': 1,
                                        'target_language_id': 1
                                    }),
                                    content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert 'error' in data
        assert 'code' in data
        assert data['code'] == 'SAME_LANGUAGE_ERROR'

    def test_update_user_languages_missing_fields(self, app, client):
        """Test language update with missing required fields."""
        with app.app_context():
            # Create test user
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()
            
            # Login the user for the request context
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
        
        # Test with missing target_language_id
        response = client.post('/api/user/languages',
                                    data=json.dumps({
                                        'native_language_id': 1
                                    }),
                                    content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert 'error' in data
        assert 'code' in data
        assert data['code'] == 'MISSING_FIELDS'

    def test_update_user_languages_invalid_language_ids(self, app, client):
        """Test language update with non-existent language IDs."""
        with app.app_context():
            # Create test user
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()
            
            # Login the user for the request context
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
        
        # Test with invalid language IDs
        response = client.post('/api/user/languages',
                                    data=json.dumps({
                                        'native_language_id': 999,
                                        'target_language_id': 998
                                    }),
                                    content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert 'error' in data
        assert 'code' in data
        assert data['code'] == 'INVALID_NATIVE_LANGUAGE'

    def test_update_user_languages_unauthenticated(self, app, client):
        """Test language update without authentication."""
        response = client.post('/api/user/languages',
                                    data=json.dumps({
                                        'native_language_id': 1,
                                        'target_language_id': 2
                                    }),
                                    content_type='application/json')
        
        # Should redirect to login or return 401
        assert response.status_code in [401, 302]

    def test_update_user_languages_invalid_json(self, app, client):
        """Test language update with invalid JSON data."""
        with app.app_context():
            # Create test user
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            db.session.commit()
            
            # Login the user for the request context
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
        
        # Test with no JSON data
        response = client.post('/api/user/languages',
                                    data="invalid json",
                                    content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert 'error' in data
        assert 'code' in data
        assert data['code'] == 'INVALID_JSON'