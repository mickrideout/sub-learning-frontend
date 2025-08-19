"""Tests for SessionAnalyticsService."""
import pytest
from datetime import datetime, date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.subtitle import UserProgress, SubLink, SubLinkLine
from app.services.session_analytics_service import SessionAnalyticsService, SessionAnalyticsServiceError


@pytest.fixture
def app():
    """Create test app instance."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Create test user."""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_sub_link(app):
    """Create test subtitle link."""
    with app.app_context():
        sub_link = SubLink(
            id=1,
            movie_title='Test Movie',
            language_from='en',
            language_to='es'
        )
        db.session.add(sub_link)
        db.session.commit()
        return sub_link


@pytest.fixture
def test_progress_records(app, test_user, test_sub_link):
    """Create test progress records."""
    with app.app_context():
        # Create progress records with different dates
        records = []
        
        # Record from 5 days ago
        record1 = UserProgress(
            user_id=test_user.id,
            sub_link_id=test_sub_link.id,
            current_alignment_index=50,
            total_alignments_completed=50,
            session_duration_minutes=30,
            last_accessed=datetime.now() - timedelta(days=5)
        )
        records.append(record1)
        
        # Record from 3 days ago
        record2 = UserProgress(
            user_id=test_user.id,
            sub_link_id=test_sub_link.id,
            current_alignment_index=100,
            total_alignments_completed=100,
            session_duration_minutes=45,
            last_accessed=datetime.now() - timedelta(days=3)
        )
        records.append(record2)
        
        # Record from today
        record3 = UserProgress(
            user_id=test_user.id,
            sub_link_id=test_sub_link.id,
            current_alignment_index=150,
            total_alignments_completed=150,
            session_duration_minutes=60,
            last_accessed=datetime.now()
        )
        records.append(record3)
        
        for record in records:
            db.session.add(record)
        
        db.session.commit()
        return records


class TestSessionAnalyticsService:
    """Test SessionAnalyticsService functionality."""
    
    def test_get_dashboard_statistics_no_data(self, app, test_user):
        """Test dashboard statistics with no progress data."""
        with app.app_context():
            stats = SessionAnalyticsService.get_dashboard_statistics(test_user.id)
            
            assert stats['total_study_minutes'] == 0
            assert stats['movies_completed'] == 0
            assert stats['total_alignments'] == 0
            assert stats['current_streak'] == 0
            assert stats['completion_rate'] == 0.0
            assert stats['avg_session_duration'] == 0.0
            assert stats['learning_velocity'] == 0.0
            assert stats['active_sessions'] == 0
            assert stats['total_sessions'] == 0
    
    def test_get_dashboard_statistics_with_data(self, app, test_user, test_progress_records):
        """Test dashboard statistics with progress data."""
        with app.app_context():
            stats = SessionAnalyticsService.get_dashboard_statistics(test_user.id)
            
            assert stats['total_study_minutes'] == 135  # 30 + 45 + 60
            assert stats['total_alignments'] == 300  # 50 + 100 + 150
            assert stats['total_sessions'] == 3
            assert stats['active_sessions'] == 3  # All have progress > 0
            assert stats['avg_session_duration'] == 45.0  # 135 / 3
            
            # Learning velocity should be > 0
            assert stats['learning_velocity'] > 0
    
    def test_calculate_learning_streak_no_data(self, app, test_user):
        """Test streak calculation with no data."""
        with app.app_context():
            streak_data = SessionAnalyticsService.calculate_learning_streak(test_user.id)
            
            assert streak_data['current_streak'] == 0
            assert streak_data['longest_streak'] == 0
            assert streak_data['last_activity_date'] is None
            assert streak_data['streak_start_date'] is None
    
    def test_calculate_learning_streak_with_data(self, app, test_user, test_progress_records):
        """Test streak calculation with progress data."""
        with app.app_context():
            streak_data = SessionAnalyticsService.calculate_learning_streak(test_user.id)
            
            # Should have some streak data
            assert streak_data['current_streak'] >= 0
            assert streak_data['longest_streak'] >= 0
            assert streak_data['last_activity_date'] is not None
    
    def test_get_progress_chart_data_weekly(self, app, test_user, test_progress_records):
        """Test weekly progress chart data generation."""
        with app.app_context():
            chart_data = SessionAnalyticsService.get_progress_chart_data(
                test_user.id, 
                period='weekly', 
                days=30
            )
            
            assert 'labels' in chart_data
            assert 'datasets' in chart_data
            assert len(chart_data['datasets']) == 2  # Study minutes and alignments
            
            # Check dataset structure
            for dataset in chart_data['datasets']:
                assert 'label' in dataset
                assert 'data' in dataset
                assert 'borderColor' in dataset
                assert 'backgroundColor' in dataset
    
    def test_get_progress_chart_data_monthly(self, app, test_user, test_progress_records):
        """Test monthly progress chart data generation."""
        with app.app_context():
            chart_data = SessionAnalyticsService.get_progress_chart_data(
                test_user.id, 
                period='monthly', 
                days=90
            )
            
            assert 'labels' in chart_data
            assert 'datasets' in chart_data
            assert len(chart_data['datasets']) == 2
    
    def test_get_session_history_no_data(self, app, test_user):
        """Test session history with no data."""
        with app.app_context():
            history = SessionAnalyticsService.get_session_history(test_user.id, limit=10, days=30)
            
            assert isinstance(history, list)
            assert len(history) == 0
    
    def test_get_session_history_with_data(self, app, test_user, test_sub_link, test_progress_records):
        """Test session history with data."""
        with app.app_context():
            history = SessionAnalyticsService.get_session_history(test_user.id, limit=10, days=30)
            
            assert isinstance(history, list)
            assert len(history) == 3  # Should match number of progress records
            
            # Check structure of history entries
            for entry in history:
                assert 'date' in entry
                assert 'datetime' in entry
                assert 'movie_title' in entry
                assert 'language_pair' in entry
                assert 'duration_minutes' in entry
                assert 'alignments_studied' in entry
                assert 'current_position' in entry
                assert 'sub_link_id' in entry
                assert 'progress_percentage' in entry
                
                # Validate data types
                assert isinstance(entry['duration_minutes'], int)
                assert isinstance(entry['alignments_studied'], int)
                assert isinstance(entry['current_position'], int)
                assert isinstance(entry['sub_link_id'], int)
                assert isinstance(entry['progress_percentage'], (int, float))
    
    def test_get_session_history_with_limit(self, app, test_user, test_progress_records):
        """Test session history with limit parameter."""
        with app.app_context():
            # Request only 2 records
            history = SessionAnalyticsService.get_session_history(test_user.id, limit=2, days=30)
            
            assert len(history) == 2
    
    def test_get_session_history_with_date_range(self, app, test_user, test_progress_records):
        """Test session history with specific date range."""
        with app.app_context():
            # Request only last 2 days (should exclude 5-day-old record)
            history = SessionAnalyticsService.get_session_history(test_user.id, limit=10, days=2)
            
            # Should have fewer records due to date filtering
            assert len(history) <= 3
    
    def test_get_learning_velocity_trends_no_data(self, app, test_user):
        """Test velocity trends with no data."""
        with app.app_context():
            trends = SessionAnalyticsService.get_learning_velocity_trends(test_user.id, days=30)
            
            assert trends['daily_velocities'] == []
            assert trends['average_velocity'] == 0.0
            assert trends['trend'] == 'stable'
    
    def test_get_learning_velocity_trends_with_data(self, app, test_user, test_progress_records):
        """Test velocity trends with data."""
        with app.app_context():
            trends = SessionAnalyticsService.get_learning_velocity_trends(test_user.id, days=30)
            
            assert isinstance(trends['daily_velocities'], list)
            assert isinstance(trends['average_velocity'], (int, float))
            assert trends['trend'] in ['stable', 'improving', 'declining']
            
            # Check structure of daily velocity entries
            for daily_velocity in trends['daily_velocities']:
                assert 'date' in daily_velocity
                assert 'velocity' in daily_velocity
                assert 'alignments' in daily_velocity
                assert 'minutes' in daily_velocity
    
    def test_calculate_progress_percentage(self, app, test_sub_link):
        """Test progress percentage calculation helper."""
        with app.app_context():
            # Create SubLinkLine with alignment data
            sub_link_line = SubLinkLine(
                sub_link_id=test_sub_link.id,
                link_data=['alignment1', 'alignment2', 'alignment3', 'alignment4', 'alignment5']  # 5 alignments
            )
            db.session.add(sub_link_line)
            db.session.commit()
            
            # Test various progress positions
            assert SessionAnalyticsService._calculate_progress_percentage(0, test_sub_link.id) == 0.0
            assert SessionAnalyticsService._calculate_progress_percentage(2, test_sub_link.id) == 40.0  # 2/5 * 100
            assert SessionAnalyticsService._calculate_progress_percentage(5, test_sub_link.id) == 100.0
            assert SessionAnalyticsService._calculate_progress_percentage(10, test_sub_link.id) == 100.0  # Capped at 100%
    
    def test_calculate_progress_percentage_no_alignments(self, app, test_sub_link):
        """Test progress percentage calculation with no alignment data."""
        with app.app_context():
            # No SubLinkLine record
            percentage = SessionAnalyticsService._calculate_progress_percentage(5, test_sub_link.id)
            assert percentage == 0.0
    
    def test_error_handling(self, app, test_user):
        """Test error handling in service methods."""
        with app.app_context():
            # Test with invalid user_id (should not raise exception)
            stats = SessionAnalyticsService.get_dashboard_statistics(99999)
            assert stats['total_study_minutes'] == 0
            
            streak_data = SessionAnalyticsService.calculate_learning_streak(99999)
            assert streak_data['current_streak'] == 0
            
            chart_data = SessionAnalyticsService.get_progress_chart_data(99999)
            assert chart_data['labels'] == []
            
            history = SessionAnalyticsService.get_session_history(99999)
            assert history == []
    
    def test_chart_data_structure(self, app, test_user, test_progress_records):
        """Test detailed structure of chart data."""
        with app.app_context():
            chart_data = SessionAnalyticsService.get_progress_chart_data(
                test_user.id, 
                period='weekly', 
                days=30
            )
            
            # Should have study minutes dataset
            study_dataset = next((d for d in chart_data['datasets'] if 'Study Minutes' in d['label']), None)
            assert study_dataset is not None
            assert isinstance(study_dataset['data'], list)
            
            # Should have alignments dataset
            alignment_dataset = next((d for d in chart_data['datasets'] if 'Alignments' in d['label']), None)
            assert alignment_dataset is not None
            assert isinstance(alignment_dataset['data'], list)
            
            # Labels and data should have same length
            assert len(chart_data['labels']) == len(study_dataset['data'])
            assert len(chart_data['labels']) == len(alignment_dataset['data'])
    
    def test_group_data_weekly_edge_cases(self, app, test_user):
        """Test weekly data grouping with edge cases."""
        with app.app_context():
            # Test with very recent date range
            chart_data = SessionAnalyticsService.get_progress_chart_data(
                test_user.id, 
                period='weekly', 
                days=7
            )
            
            # Should still return proper structure even with no data
            assert 'labels' in chart_data
            assert 'datasets' in chart_data
    
    def test_group_data_monthly_edge_cases(self, app, test_user):
        """Test monthly data grouping with edge cases."""
        with app.app_context():
            # Test with short date range
            chart_data = SessionAnalyticsService.get_progress_chart_data(
                test_user.id, 
                period='monthly', 
                days=10
            )
            
            # Should still return proper structure
            assert 'labels' in chart_data
            assert 'datasets' in chart_data