"""Tests for bookmark API endpoints."""
import pytest
import json
from app import create_app, db
from app.models.user import User
from app.models.language import Language
from app.models.subtitle import SubTitle, SubLink, SubLinkLine, SubLine
from app.models.bookmark import Bookmark


@pytest.fixture
def app():
    """Create test application."""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'GOOGLE_CLIENT_ID': 'test-client-id',
        'GOOGLE_CLIENT_SECRET': 'test-client-secret',
        'FACEBOOK_CLIENT_ID': 'test-facebook-id',
        'FACEBOOK_CLIENT_SECRET': 'test-facebook-secret',
        'APPLE_CLIENT_ID': 'test-apple-id',
        'APPLE_PRIVATE_KEY': 'test-apple-key'
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_data(app):
    """Create sample data for testing."""
    with app.app_context():
        # Create languages
        lang1 = Language(id=1, name='english', display_name='English', code='en')
        lang2 = Language(id=2, name='spanish', display_name='Spanish', code='es')
        db.session.add_all([lang1, lang2])
        
        # Create user
        user = User(
            email='test@example.com',
            password_hash='hashed_password',
            is_active=True,
            email_verified=True,
            native_language_id=lang1.id,
            target_language_id=lang2.id
        )
        db.session.add(user)
        
        # Create subtitles
        subtitle1 = SubTitle(id=1, title='Test Movie 1')
        subtitle2 = SubTitle(id=2, title='Test Movie 2')
        db.session.add_all([subtitle1, subtitle2])
        
        # Create sub_link
        sub_link = SubLink(
            id=1,
            fromid=subtitle1.id,
            fromlang=lang1.id,
            toid=subtitle2.id,
            tolang=lang2.id
        )
        db.session.add(sub_link)
        
        # Create subtitle lines
        source_line = SubLine(
            id=101,
            movie_id=subtitle1.id,
            sequence=1,
            content='Hello world',
            language_id=lang1.id
        )
        target_line = SubLine(
            id=102,
            movie_id=subtitle2.id,
            sequence=1,
            content='Hola mundo',
            language_id=lang2.id
        )
        db.session.add_all([source_line, target_line])
        
        # Create alignment data
        sub_link_line = SubLinkLine(
            id=1,
            sub_link_id=sub_link.id,
            link_data=[
                [[101], [102]],  # First alignment pair
                [[101], [102]],  # Second alignment pair
                [[101], [102]]   # Third alignment pair
            ]
        )
        db.session.add(sub_link_line)
        
        db.session.commit()
        
        return {
            'user': user,
            'sub_link': sub_link,
            'sub_link_line': sub_link_line,
            'lang1': lang1,
            'lang2': lang2
        }


@pytest.fixture
def logged_in_user(client, sample_data):
    """Log in a user for testing."""
    with client.session_transaction() as sess:
        sess['user_id'] = str(sample_data['user'].id)
        sess['_fresh'] = True
    return sample_data['user']


def test_create_bookmark_success(client, sample_data, logged_in_user):
    """Test successful bookmark creation."""
    data = {
        'sub_link_id': sample_data['sub_link'].id,
        'alignment_index': 0,
        'note': 'Test bookmark note'
    }
    
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    
    assert response_data['message'] == 'Bookmark created successfully'
    assert 'bookmark' in response_data
    assert response_data['bookmark']['alignment_index'] == 0
    assert response_data['bookmark']['note'] == 'Test bookmark note'


def test_create_bookmark_missing_data(client, sample_data, logged_in_user):
    """Test bookmark creation with missing required data."""
    data = {
        'alignment_index': 0
        # Missing sub_link_id
    }
    
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['code'] == 'MISSING_SUB_LINK_ID'


def test_create_bookmark_invalid_json(client, logged_in_user):
    """Test bookmark creation with invalid JSON."""
    response = client.post(
        '/api/bookmarks',
        data='invalid json',
        content_type='application/json'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['code'] == 'INVALID_JSON'


def test_create_bookmark_duplicate(client, sample_data, logged_in_user):
    """Test duplicate bookmark creation."""
    data = {
        'sub_link_id': sample_data['sub_link'].id,
        'alignment_index': 0
    }
    
    # Create first bookmark
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 201
    
    # Try to create duplicate
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 409
    response_data = json.loads(response.data)
    assert response_data['code'] == 'BOOKMARK_ALREADY_EXISTS'


def test_create_bookmark_unauthorized(client, sample_data):
    """Test bookmark creation without authentication."""
    data = {
        'sub_link_id': sample_data['sub_link'].id,
        'alignment_index': 0
    }
    
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 401


def test_get_bookmarks_empty(client, sample_data, logged_in_user):
    """Test getting bookmarks when user has none."""
    response = client.get('/api/bookmarks')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['bookmarks'] == []
    assert response_data['total_count'] == 0
    assert response_data['has_more'] is False


def test_get_bookmarks_with_data(client, sample_data, logged_in_user):
    """Test getting bookmarks with existing data."""
    # Create test bookmarks
    bookmark1 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='First bookmark'
    )
    bookmark2 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=1,
        note='Second bookmark'
    )
    db.session.add_all([bookmark1, bookmark2])
    db.session.commit()
    
    response = client.get('/api/bookmarks')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['total_count'] == 2
    assert len(response_data['bookmarks']) == 2


def test_get_bookmarks_pagination(client, sample_data, logged_in_user):
    """Test bookmark pagination."""
    # Create multiple bookmarks
    for i in range(5):
        bookmark = Bookmark(
            user_id=sample_data['user'].id,
            sub_link_id=sample_data['sub_link'].id,
            alignment_index=i,
            note=f'Bookmark {i}'
        )
        db.session.add(bookmark)
    db.session.commit()
    
    # Test first page
    response = client.get('/api/bookmarks?limit=3&offset=0')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['total_count'] == 5
    assert len(response_data['bookmarks']) == 3
    assert response_data['has_more'] is True


def test_get_bookmarks_search(client, sample_data, logged_in_user):
    """Test bookmark search."""
    # Create bookmarks with different notes
    bookmark1 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='Important grammar rule'
    )
    bookmark2 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=1,
        note='Vocabulary word'
    )
    db.session.add_all([bookmark1, bookmark2])
    db.session.commit()
    
    response = client.get('/api/bookmarks?search=grammar')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['total_count'] == 1
    assert 'grammar' in response_data['bookmarks'][0]['note'].lower()


def test_get_bookmarks_unauthorized(client):
    """Test getting bookmarks without authentication."""
    response = client.get('/api/bookmarks')
    assert response.status_code == 401


def test_delete_bookmark_success(client, sample_data, logged_in_user):
    """Test successful bookmark deletion."""
    # Create bookmark
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0
    )
    db.session.add(bookmark)
    db.session.commit()
    
    response = client.delete(f'/api/bookmarks/{bookmark.id}')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['message'] == 'Bookmark deleted successfully'
    assert response_data['bookmark_id'] == bookmark.id
    
    # Verify bookmark is soft deleted
    db.session.refresh(bookmark)
    assert bookmark.is_active is False


def test_delete_bookmark_not_found(client, sample_data, logged_in_user):
    """Test deleting non-existent bookmark."""
    response = client.delete('/api/bookmarks/999')
    
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert response_data['code'] == 'BOOKMARK_NOT_FOUND'


def test_delete_bookmark_unauthorized(client, sample_data):
    """Test deleting bookmark without authentication."""
    response = client.delete('/api/bookmarks/1')
    assert response.status_code == 401


def test_search_bookmarks_success(client, sample_data, logged_in_user):
    """Test bookmark search endpoint."""
    # Create bookmarks
    bookmark1 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='Python programming language'
    )
    bookmark2 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=1,
        note='JavaScript is also programming'
    )
    db.session.add_all([bookmark1, bookmark2])
    db.session.commit()
    
    response = client.get('/api/bookmarks/search?q=programming')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['search_query'] == 'programming'
    assert response_data['count'] == 2
    assert len(response_data['results']) == 2


def test_search_bookmarks_missing_query(client, logged_in_user):
    """Test search without query parameter."""
    response = client.get('/api/bookmarks/search')
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['code'] == 'MISSING_SEARCH_QUERY'


def test_search_bookmarks_unauthorized(client):
    """Test search without authentication."""
    response = client.get('/api/bookmarks/search?q=test')
    assert response.status_code == 401


def test_export_bookmarks_success(client, sample_data, logged_in_user):
    """Test bookmark export."""
    # Create bookmark
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='Test export note'
    )
    db.session.add(bookmark)
    db.session.commit()
    
    response = client.get('/api/bookmarks/export?format=text')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data['format'] == 'text'
    assert 'export_data' in response_data
    assert 'Test export note' in response_data['export_data']


def test_export_bookmarks_unsupported_format(client, logged_in_user):
    """Test export with unsupported format."""
    response = client.get('/api/bookmarks/export?format=json')
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['code'] == 'UNSUPPORTED_FORMAT'


def test_export_bookmarks_unauthorized(client):
    """Test export without authentication."""
    response = client.get('/api/bookmarks/export')
    assert response.status_code == 401


def test_bookmark_endpoints_error_handling(client, sample_data, logged_in_user):
    """Test error handling in bookmark endpoints."""
    # Test invalid alignment index
    data = {
        'sub_link_id': sample_data['sub_link'].id,
        'alignment_index': -1
    }
    
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['code'] == 'INVALID_BOOKMARK_DATA'


def test_bookmark_endpoints_field_validation(client, sample_data, logged_in_user):
    """Test field validation in bookmark endpoints."""
    # Test invalid field types
    data = {
        'sub_link_id': 'invalid',
        'alignment_index': 'also_invalid'
    }
    
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['code'] == 'INVALID_FIELD_VALUES'