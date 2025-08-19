"""Tests for progress service business logic."""
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.language import Language
from app.models.subtitle import SubTitle, SubLink, SubLinkLine, UserProgress
from app.services.progress_service import ProgressService, ProgressServiceError


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
def sample_subtitle_data(app):
    """Create sample subtitle data for testing."""
    with app.app_context():
        # Create languages first
        lang1 = Language(id=1, name='english', display_name='English', code='en')
        lang2 = Language(id=2, name='spanish', display_name='Spanish', code='es')
        db.session.add_all([lang1, lang2])
        db.session.flush()
        
        # Create user
        user = User(
            email='testuser@example.com',
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
        
        # Create alignment data with 10 items
        alignment_data = [
            [["Hello"], ["Hola"]],
            [["How are you?"], ["¿Cómo estás?"]],
            [["Good morning"], ["Buenos días"]],
            [["Thank you"], ["Gracias"]],
            [["Goodbye"], ["Adiós"]],
            [["Please"], ["Por favor"]],
            [["Excuse me"], ["Perdón"]],
            [["Yes"], ["Sí"]],
            [["No"], ["No"]],
            [["Maybe"], ["Tal vez"]]
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
            'sub_link': sub_link
        }


class TestProgressService:
    """Test suite for ProgressService business logic."""
    
    def test_get_user_progress_not_found(self, app, sample_subtitle_data):
        """Test getting progress when none exists."""
        with app.app_context():
            result = ProgressService.get_user_progress(
                sample_subtitle_data['user_id'],
                sample_subtitle_data['sub_link_id']
            )
            assert result is None
    
    def test_get_user_progress_invalid_sub_link(self, app, sample_subtitle_data):
        """Test getting progress for non-existent sub_link."""
        with app.app_context():
            with pytest.raises(ProgressServiceError) as exc_info:
                ProgressService.get_user_progress(
                    sample_subtitle_data['user_id'],
                    99999
                )
            assert "not found" in str(exc_info.value)
    
    def test_get_user_progress_existing(self, app, sample_subtitle_data):
        """Test getting existing progress."""
        with app.app_context():
            # Create progress record
            progress = UserProgress(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=5,
                total_alignments_completed=5,
                session_duration_minutes=30
            )
            db.session.add(progress)
            db.session.commit()
            
            # Get progress
            result = ProgressService.get_user_progress(
                sample_subtitle_data['user_id'],
                sample_subtitle_data['sub_link_id']
            )
            
            assert result is not None
            assert result['current_alignment_index'] == 5
            assert result['total_alignments_completed'] == 5
            assert result['session_duration_minutes'] == 30
            assert result['completion_percentage'] == 50.0  # 5/10 * 100
            assert result['total_alignments'] == sample_subtitle_data['total_alignments']
    
    def test_update_progress_new_record(self, app, sample_subtitle_data):
        """Test creating new progress record."""
        with app.app_context():
            result = ProgressService.update_progress(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=3,
                session_duration_minutes=15
            )
            
            assert result['current_alignment_index'] == 3
            assert result['total_alignments_completed'] == 3
            assert result['session_duration_minutes'] == 15
            assert result['completion_percentage'] == 30.0  # 3/10 * 100
            
            # Verify in database
            progress = UserProgress.query.filter_by(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id']
            ).first()
            assert progress is not None
            assert progress.current_alignment_index == 3
    
    def test_update_progress_existing_record(self, app, sample_subtitle_data):
        """Test updating existing progress record."""
        with app.app_context():
            # Create initial progress
            initial_progress = UserProgress(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=2,
                total_alignments_completed=2,
                session_duration_minutes=10
            )
            db.session.add(initial_progress)
            db.session.commit()
            
            # Update progress
            result = ProgressService.update_progress(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=7,
                session_duration_minutes=20
            )
            
            assert result['current_alignment_index'] == 7
            assert result['total_alignments_completed'] == 7  # Should be max(2, 7)
            assert result['session_duration_minutes'] == 30  # 10 + 20
            assert result['completion_percentage'] == 70.0  # 7/10 * 100
    
    def test_update_progress_backward_movement(self, app, sample_subtitle_data):
        """Test updating progress when user moves backward."""
        with app.app_context():
            # Create progress at position 8
            initial_progress = UserProgress(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=8,
                total_alignments_completed=8,
                session_duration_minutes=40
            )
            db.session.add(initial_progress)
            db.session.commit()
            
            # Move backward to position 5
            result = ProgressService.update_progress(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=5,
                session_duration_minutes=10
            )
            
            assert result['current_alignment_index'] == 5
            assert result['total_alignments_completed'] == 8  # Should remain at max
            assert result['session_duration_minutes'] == 50  # 40 + 10
            assert result['completion_percentage'] == 50.0  # 5/10 * 100
    
    def test_update_progress_invalid_sub_link(self, app, sample_subtitle_data):
        """Test updating progress for non-existent sub_link."""
        with app.app_context():
            with pytest.raises(ProgressServiceError) as exc_info:
                ProgressService.update_progress(
                    user_id=sample_subtitle_data['user_id'],
                    sub_link_id=99999,
                    current_alignment_index=1,
                    session_duration_minutes=5
                )
            assert "not found" in str(exc_info.value)
    
    def test_update_progress_negative_values(self, app, sample_subtitle_data):
        """Test updating progress with negative values."""
        with app.app_context():
            # Test negative alignment index
            with pytest.raises(ProgressServiceError) as exc_info:
                ProgressService.update_progress(
                    user_id=sample_subtitle_data['user_id'],
                    sub_link_id=sample_subtitle_data['sub_link_id'],
                    current_alignment_index=-1,
                    session_duration_minutes=5
                )
            assert "cannot be negative" in str(exc_info.value)
            
            # Test negative session duration
            with pytest.raises(ProgressServiceError) as exc_info:
                ProgressService.update_progress(
                    user_id=sample_subtitle_data['user_id'],
                    sub_link_id=sample_subtitle_data['sub_link_id'],
                    current_alignment_index=1,
                    session_duration_minutes=-5
                )
            assert "cannot be negative" in str(exc_info.value)
    
    def test_update_progress_exceeds_total(self, app, sample_subtitle_data):
        """Test updating progress beyond total alignments."""
        with app.app_context():
            with pytest.raises(ProgressServiceError) as exc_info:
                ProgressService.update_progress(
                    user_id=sample_subtitle_data['user_id'],
                    sub_link_id=sample_subtitle_data['sub_link_id'],
                    current_alignment_index=sample_subtitle_data['total_alignments'] + 5,
                    session_duration_minutes=5
                )
            assert "exceeds total alignments" in str(exc_info.value)
    
    def test_calculate_completion_percentage(self):
        """Test completion percentage calculation."""
        # Normal case
        assert ProgressService.calculate_completion_percentage(5, 10) == 50.0
        assert ProgressService.calculate_completion_percentage(0, 10) == 0.0
        assert ProgressService.calculate_completion_percentage(10, 10) == 100.0
        
        # Edge cases
        assert ProgressService.calculate_completion_percentage(0, 0) == 0.0
        assert ProgressService.calculate_completion_percentage(5, 0) == 0.0
        
        # Rounding
        assert ProgressService.calculate_completion_percentage(1, 3) == 33.33
        assert ProgressService.calculate_completion_percentage(2, 3) == 66.67
    
    def test_get_recent_progress_empty(self, app, sample_subtitle_data):
        """Test getting recent progress when none exists."""
        with app.app_context():
            result = ProgressService.get_recent_progress(sample_subtitle_data['user_id'])
            assert result == []
    
    def test_get_recent_progress_with_data(self, app):
        """Test getting recent progress with existing data."""
        with app.app_context():
            # Create languages and user first
            lang1 = Language(id=1, name='english', display_name='English', code='en')
            lang2 = Language(id=2, name='spanish', display_name='Spanish', code='es')
            db.session.add_all([lang1, lang2])
            
            user = User(
                email='testuser_recent@example.com',
                password_hash='hashed_password',
                is_active=True,
                email_verified=True,
                native_language_id=lang1.id,
                target_language_id=lang2.id
            )
            db.session.add(user)
            db.session.flush()
            
            # Create multiple subtitle links for different progress records
            progress_records = []
            for i in range(3):  # Reduced to avoid complexity
                # Create unique subtitle and sub_link for each progress record
                subtitle = SubTitle(title=f'Test Movie {i}')
                db.session.add(subtitle)
                db.session.flush()
                
                sub_link = SubLink(
                    fromid=subtitle.id,
                    fromlang=user.native_language_id,
                    toid=subtitle.id,
                    tolang=user.target_language_id
                )
                db.session.add(sub_link)
                db.session.flush()
                
                # Create alignment data
                sub_link_line = SubLinkLine(
                    sub_link_id=sub_link.id,
                    link_data=[[["Hello"], ["Hola"]], [["Goodbye"], ["Adiós"]]]
                )
                db.session.add(sub_link_line)
                
                progress = UserProgress(
                    user_id=user.id,
                    sub_link_id=sub_link.id,
                    current_alignment_index=i + 1,
                    total_alignments_completed=i + 1,
                    session_duration_minutes=(i + 1) * 5,
                    last_accessed=datetime.utcnow() - timedelta(days=i)
                )
                progress_records.append(progress)
            
            db.session.add_all(progress_records)
            db.session.commit()
            
            # Get recent progress
            result = ProgressService.get_recent_progress(user.id, limit=3)
            
            assert len(result) == 3  # Limited to 3 records
            
            # Should be sorted by last_accessed descending (most recent first)
            for i in range(len(result) - 1):
                current_date = datetime.fromisoformat(result[i]['last_accessed'])
                next_date = datetime.fromisoformat(result[i + 1]['last_accessed'])
                assert current_date >= next_date
            
            # Verify data structure
            for progress_item in result:
                assert 'current_alignment_index' in progress_item
                assert 'completion_percentage' in progress_item
                assert 'total_alignments' in progress_item
                assert 'session_duration_minutes' in progress_item
    
    def test_get_recent_progress_with_limit(self, app):
        """Test getting recent progress with different limits."""
        with app.app_context():
            # Create languages and user first
            lang1 = Language(id=3, name='french', display_name='French', code='fr')
            lang2 = Language(id=4, name='german', display_name='German', code='de')
            db.session.add_all([lang1, lang2])
            
            user = User(
                email='testuser_limit@example.com',
                password_hash='hashed_password',
                is_active=True,
                email_verified=True,
                native_language_id=lang1.id,
                target_language_id=lang2.id
            )
            db.session.add(user)
            db.session.flush()
            
            # Create 5 progress records with different sub_links
            progress_records = []
            for i in range(5):
                # Create unique subtitle and sub_link for each progress record
                subtitle = SubTitle(title=f'Limit Test Movie {i}')
                db.session.add(subtitle)
                db.session.flush()
                
                sub_link = SubLink(
                    fromid=subtitle.id,
                    fromlang=user.native_language_id,
                    toid=subtitle.id,
                    tolang=user.target_language_id
                )
                db.session.add(sub_link)
                db.session.flush()
                
                # Create alignment data
                sub_link_line = SubLinkLine(
                    sub_link_id=sub_link.id,
                    link_data=[[["Bonjour"], ["Hallo"]], [["Au revoir"], ["Auf Wiedersehen"]]]
                )
                db.session.add(sub_link_line)
                
                progress = UserProgress(
                    user_id=user.id,
                    sub_link_id=sub_link.id,
                    current_alignment_index=i,
                    total_alignments_completed=i,
                    session_duration_minutes=i * 2,
                    last_accessed=datetime.utcnow() - timedelta(hours=i)
                )
                progress_records.append(progress)
            
            db.session.add_all(progress_records)
            db.session.commit()
            
            # Test different limits
            result_3 = ProgressService.get_recent_progress(user.id, limit=3)
            assert len(result_3) == 3
            
            result_10 = ProgressService.get_recent_progress(user.id, limit=10)
            assert len(result_10) == 5  # Only 5 records exist
            
            result_default = ProgressService.get_recent_progress(user.id)
            assert len(result_default) == 5  # Default limit should show all
    
    def test_progress_statistics_accuracy(self, app, sample_subtitle_data):
        """Test accuracy of progress statistics calculations."""
        with app.app_context():
            # Create progress at exactly 50%
            result = ProgressService.update_progress(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=5,
                session_duration_minutes=25
            )
            
            assert result['completion_percentage'] == 50.0
            assert result['total_alignments'] == 10
            assert result['current_alignment_index'] == 5
            
            # Move to 100%
            result = ProgressService.update_progress(
                user_id=sample_subtitle_data['user_id'],
                sub_link_id=sample_subtitle_data['sub_link_id'],
                current_alignment_index=10,
                session_duration_minutes=15
            )
            
            assert result['completion_percentage'] == 100.0
            assert result['session_duration_minutes'] == 40  # 25 + 15
            assert result['total_alignments_completed'] == 10
    
    def test_database_transaction_integrity(self, app):
        """Test that progress updates maintain database integrity."""
        with app.app_context():
            # Create test data
            lang1 = Language(id=5, name='italian', display_name='Italian', code='it')
            lang2 = Language(id=6, name='portuguese', display_name='Portuguese', code='pt')
            db.session.add_all([lang1, lang2])
            
            user = User(
                email='testuser_integrity@example.com',
                password_hash='hashed_password',
                is_active=True,
                email_verified=True,
                native_language_id=lang1.id,
                target_language_id=lang2.id
            )
            db.session.add(user)
            
            subtitle = SubTitle(title='Integrity Test Movie')
            db.session.add(subtitle)
            db.session.flush()
            
            sub_link = SubLink(
                fromid=subtitle.id,
                fromlang=user.native_language_id,
                toid=subtitle.id,
                tolang=user.target_language_id
            )
            db.session.add(sub_link)
            db.session.flush()
            
            sub_link_line = SubLinkLine(
                sub_link_id=sub_link.id,
                link_data=[[["Ciao"], ["Olá"]], [["Arrivederci"], ["Tchau"]]]
            )
            db.session.add(sub_link_line)
            db.session.commit()
            
            # Test successful transaction
            result = ProgressService.update_progress(
                user_id=user.id,
                sub_link_id=sub_link.id,
                current_alignment_index=1,
                session_duration_minutes=15
            )
            
            # Verify the record was created
            progress = UserProgress.query.filter_by(
                user_id=user.id,
                sub_link_id=sub_link.id
            ).first()
            
            assert progress is not None
            assert progress.current_alignment_index == 1
            assert progress.session_duration_minutes == 15