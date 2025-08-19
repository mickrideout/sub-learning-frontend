"""Tests for progress API endpoints."""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.language import Language
from app.models.subtitle import SubTitle, SubLink, SubLinkLine, UserProgress


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
def auth_headers():
    """Create authentication headers."""
    return {'Content-Type': 'application/json'}


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        # Create languages first
        lang1 = Language(id=1, name='english', display_name='English', code='en')
        lang2 = Language(id=2, name='spanish', display_name='Spanish', code='es')
        db.session.add_all([lang1, lang2])
        db.session.flush()
        
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
        db.session.commit()
        return user


@pytest.fixture
def sample_data(app):
    """Create sample data for API testing."""
    with app.app_context():
        # Create languages first
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
        db.session.flush()
        
        # Create subtitle
        subtitle = SubTitle(title='Test Movie')
        db.session.add(subtitle)
        db.session.flush()
        
        # Create sub_link
        sub_link = SubLink(
            fromid=subtitle.id,
            fromlang=user.native_language_id,
            toid=subtitle.id,
            tolang=user.target_language_id
        )
        db.session.add(sub_link)
        db.session.flush()
        
        # Create alignment data
        alignment_data = [
            [["Hello"], ["Hola"]],
            [["How are you?"], ["¿Cómo estás?"]],
            [["Good morning"], ["Buenos días"]],
            [["Thank you"], ["Gracias"]],
            [["Goodbye"], ["Adiós"]]
        ]
        
        sub_link_line = SubLinkLine(
            sub_link_id=sub_link.id,
            link_data=alignment_data
        )
        db.session.add(sub_link_line)
        db.session.commit()
        
        return {
            'user_id': user.id,
            'sub_link_id': sub_link.id,
            'total_alignments': len(alignment_data),
            'subtitle': subtitle,
            'sub_link': sub_link,
            'user': user
        }


class TestProgressEndpoints:
    """Test suite for progress API endpoints."""
    
    def test_get_progress_not_found(self, client, sample_data):
        """Test GET progress when no progress exists."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_data['user_id']
            sess['_fresh'] = True
        
        response = client.get(f"/api/progress/{sample_data['sub_link_id']}")
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['code'] == 'NO_PROGRESS_FOUND'
    
    def test_get_progress_invalid_sub_link(self, client, sample_user):
        """Test GET progress with invalid sub_link_id."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        response = client.get("/api/progress/99999")
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'not found' in data['error'].lower()
    
    def test_create_progress_valid(self, client, sample_user, sample_subtitle_data, app):
        """Test creating new progress record."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        progress_data = {
            'current_alignment_index': 2,
            'session_duration_minutes': 15
        }
        
        response = client.put(
            f"/api/progress/{sample_subtitle_data['sub_link_id']}",
            data=json.dumps(progress_data),
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['message'] == 'Progress updated successfully'
        assert data['progress']['current_alignment_index'] == 2
        assert data['progress']['total_alignments_completed'] == 2
        assert data['progress']['session_duration_minutes'] == 15
        assert 'completion_percentage' in data['progress']
        
        # Verify in database
        with app.app_context():
            progress = UserProgress.query.filter_by(
                user_id=sample_user.id,
                sub_link_id=sample_subtitle_data['sub_link_id']
            ).first()
            assert progress is not None
            assert progress.current_alignment_index == 2
    
    def test_update_existing_progress(self, client, sample_user, sample_subtitle_data, app):
        """Test updating existing progress record."""
        # First create initial progress
        with app.app_context():
            initial_progress = UserProgress(
                user_id=sample_user.id,
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=1,
                total_alignments_completed=1,
                session_duration_minutes=10
            )
            db.session.add(initial_progress)
            db.session.commit()
        
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        # Update progress
        progress_data = {
            'current_alignment_index': 3,
            'session_duration_minutes': 20
        }
        
        response = client.put(
            f"/api/progress/{sample_subtitle_data['sub_link_id']}",
            data=json.dumps(progress_data),
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['progress']['current_alignment_index'] == 3
        assert data['progress']['total_alignments_completed'] == 3  # Should be max of previous and current
        assert data['progress']['session_duration_minutes'] == 30  # 10 + 20
        
        # Verify in database
        with app.app_context():
            progress = UserProgress.query.filter_by(
                user_id=sample_user.id,
                sub_link_id=sample_subtitle_data['sub_link_id']
            ).first()
            assert progress.current_alignment_index == 3
            assert progress.session_duration_minutes == 30
    
    def test_get_existing_progress(self, client, sample_user, sample_subtitle_data, app):
        """Test GET existing progress."""
        # Create progress record
        with app.app_context():
            progress = UserProgress(
                user_id=sample_user.id,
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=2,
                total_alignments_completed=2,
                session_duration_minutes=25
            )
            db.session.add(progress)
            db.session.commit()
        
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        response = client.get(f"/api/progress/{sample_subtitle_data['sub_link_id']}")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['progress']['current_alignment_index'] == 2
        assert data['progress']['total_alignments_completed'] == 2
        assert data['progress']['session_duration_minutes'] == 25
        assert 'completion_percentage' in data['progress']
        assert data['progress']['total_alignments'] == sample_subtitle_data['total_alignments']
    
    def test_update_progress_invalid_data(self, client, sample_user, sample_subtitle_data):
        """Test updating progress with invalid data."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        # Test missing required field
        response = client.put(
            f"/api/progress/{sample_subtitle_data['sub_link_id']}",
            data=json.dumps({}),
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'MISSING_ALIGNMENT_INDEX'
        
        # Test negative alignment index
        response = client.put(
            f"/api/progress/{sample_subtitle_data['sub_link_id']}",
            data=json.dumps({'current_alignment_index': -1}),
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'non-negative' in data['error']
    
    def test_update_progress_exceeds_total(self, client, sample_user, sample_subtitle_data):
        """Test updating progress beyond total alignments."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        progress_data = {
            'current_alignment_index': sample_subtitle_data['total_alignments'] + 10,
            'session_duration_minutes': 5
        }
        
        response = client.put(
            f"/api/progress/{sample_subtitle_data['sub_link_id']}",
            data=json.dumps(progress_data),
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'exceeds total alignments' in data['error']
    
    def test_get_recent_progress_empty(self, client, sample_user):
        """Test GET recent progress when no progress exists."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        response = client.get("/api/progress/recent")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['recent_progress'] == []
        assert data['count'] == 0
    
    def test_get_recent_progress_with_data(self, client, sample_user, sample_subtitle_data, app):
        """Test GET recent progress with existing data."""
        # Create multiple progress records
        with app.app_context():
            progress_records = []
            for i in range(3):
                progress = UserProgress(
                    user_id=sample_user.id,
                    sub_link_id=sample_subtitle_data['sub_link_id'],
                    current_alignment_index=i + 1,
                    total_alignments_completed=i + 1,
                    session_duration_minutes=(i + 1) * 10,
                    last_accessed=datetime.utcnow() - timedelta(days=i)
                )
                progress_records.append(progress)
            
            db.session.add_all(progress_records)
            db.session.commit()
        
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        response = client.get("/api/progress/recent")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['recent_progress']) >= 1  # At least one record
        assert data['count'] >= 1
        
        # Verify data structure
        for progress_item in data['recent_progress']:
            assert 'current_alignment_index' in progress_item
            assert 'completion_percentage' in progress_item
            assert 'total_alignments' in progress_item
    
    def test_get_recent_progress_with_limit(self, client, sample_user, sample_subtitle_data, app):
        """Test GET recent progress with limit parameter."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        response = client.get("/api/progress/recent?limit=2")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['recent_progress']) <= 2
    
    def test_progress_unauthorized(self, client, sample_subtitle_data):
        """Test progress endpoints without authentication."""
        # Test GET without auth
        response = client.get(f"/api/progress/{sample_subtitle_data['sub_link_id']}")
        assert response.status_code == 401
        
        # Test PUT without auth
        response = client.put(
            f"/api/progress/{sample_subtitle_data['sub_link_id']}",
            data=json.dumps({'current_alignment_index': 1}),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 401
        
        # Test recent progress without auth
        response = client.get("/api/progress/recent")
        assert response.status_code == 401
    
    def test_completion_percentage_calculation(self, client, sample_user, sample_subtitle_data):
        """Test completion percentage calculation accuracy."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        total_alignments = sample_subtitle_data['total_alignments']
        
        # Test 50% completion
        progress_data = {
            'current_alignment_index': total_alignments // 2,
            'session_duration_minutes': 10
        }
        
        response = client.put(
            f"/api/progress/{sample_subtitle_data['sub_link_id']}",
            data=json.dumps(progress_data),
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        expected_percentage = (total_alignments // 2) / total_alignments * 100
        assert abs(data['progress']['completion_percentage'] - expected_percentage) < 1.0
    
    def test_invalid_json_data(self, client, sample_user, sample_subtitle_data):
        """Test handling of invalid JSON data."""
        with client.session_transaction() as sess:
            sess['user_id'] = sample_user.id
            sess['_fresh'] = True
        
        response = client.put(
            f"/api/progress/{sample_subtitle_data['sub_link_id']}",
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 'INVALID_JSON'