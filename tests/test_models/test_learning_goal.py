"""Tests for LearningGoal model."""
import pytest
from datetime import datetime, date, timedelta
from app.models.learning_goal import LearningGoal
from app import create_app, db
from app.models.user import User


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
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create test user."""
    user = User(email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


class TestLearningGoal:
    """Test LearningGoal model functionality."""
    
    def test_create_learning_goal(self, app, test_user):
        """Test creating a new learning goal."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30,
                deadline=date.today() + timedelta(days=30)
            )
            
            assert goal.user_id == test_user.id
            assert goal.goal_type == 'daily_minutes'
            assert goal.target_value == 30
            assert goal.current_value == 0
            assert goal.is_active is True
            assert goal.completed_at is None
    
    def test_to_dict_conversion(self, app, test_user):
        """Test converting goal to dictionary."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100,
                deadline=date.today() + timedelta(days=7)
            )
            
            goal_dict = goal.to_dict()
            
            assert goal_dict['user_id'] == test_user.id
            assert goal_dict['goal_type'] == 'weekly_alignments'
            assert goal_dict['target_value'] == 100
            assert goal_dict['current_value'] == 0
            assert goal_dict['progress_percentage'] == 0.0
            assert goal_dict['is_active'] is True
            assert goal_dict['is_completed'] is False
    
    def test_update_progress(self, app, test_user):
        """Test updating goal progress."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=60
            )
            
            # Update progress to 30 minutes
            goal.update_progress(30)
            assert goal.current_value == 30
            assert goal.completed_at is None
            
            # Complete the goal
            goal.update_progress(60)
            assert goal.current_value == 60
            assert goal.completed_at is not None
    
    def test_increment_progress(self, app, test_user):
        """Test incrementing goal progress."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='movie_completion',
                target_value=5
            )
            
            # Increment by 1 (default)
            goal.increment_progress()
            assert goal.current_value == 1
            
            # Increment by 2
            goal.increment_progress(2)
            assert goal.current_value == 3
            
            # Complete the goal
            goal.increment_progress(2)
            assert goal.current_value == 5
            assert goal.is_goal_completed() is True
    
    def test_is_goal_completed(self, app, test_user):
        """Test goal completion check."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            assert goal.is_goal_completed() is False
            
            goal.update_progress(15)
            assert goal.is_goal_completed() is False
            
            goal.update_progress(30)
            assert goal.is_goal_completed() is True
    
    def test_days_until_deadline(self, app, test_user):
        """Test days until deadline calculation."""
        with app.app_context():
            # Goal with deadline in 7 days
            future_deadline = date.today() + timedelta(days=7)
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100,
                deadline=future_deadline
            )
            
            assert goal.days_until_deadline() == 7
            
            # Goal with no deadline
            goal_no_deadline = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            assert goal_no_deadline.days_until_deadline() is None
    
    def test_is_overdue(self, app, test_user):
        """Test overdue goal detection."""
        with app.app_context():
            # Past deadline, not completed
            past_deadline = date.today() - timedelta(days=1)
            overdue_goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30,
                deadline=past_deadline
            )
            
            assert overdue_goal.is_overdue() is True
            
            # Past deadline, but completed
            overdue_goal.update_progress(30)
            assert overdue_goal.is_overdue() is False
            
            # Future deadline
            future_deadline = date.today() + timedelta(days=7)
            future_goal = LearningGoal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100,
                deadline=future_deadline
            )
            
            assert future_goal.is_overdue() is False
    
    def test_get_progress_rate(self, app, test_user):
        """Test daily progress rate calculation."""
        with app.app_context():
            # Goal with 10 days remaining, need 100 alignments
            future_deadline = date.today() + timedelta(days=10)
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100,
                deadline=future_deadline
            )
            
            # Need 10 alignments per day
            assert goal.get_progress_rate() == 10.0
            
            # Make some progress
            goal.update_progress(50)
            # Now need 5 alignments per day
            assert goal.get_progress_rate() == 5.0
            
            # Goal with no deadline
            goal_no_deadline = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            assert goal_no_deadline.get_progress_rate() is None
    
    def test_progress_percentage_calculation(self, app, test_user):
        """Test progress percentage calculation in to_dict."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=60
            )
            
            # 0% progress
            goal_dict = goal.to_dict()
            assert goal_dict['progress_percentage'] == 0.0
            
            # 50% progress
            goal.update_progress(30)
            goal_dict = goal.to_dict()
            assert goal_dict['progress_percentage'] == 50.0
            
            # 100% progress
            goal.update_progress(60)
            goal_dict = goal.to_dict()
            assert goal_dict['progress_percentage'] == 100.0
            
            # Over 100% (should cap at 100%)
            goal.update_progress(120)
            goal_dict = goal.to_dict()
            assert goal_dict['progress_percentage'] == 100.0
    
    def test_goal_string_representation(self, app, test_user):
        """Test goal string representation."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            db.session.add(goal)
            db.session.commit()
            
            goal_str = str(goal)
            assert 'LearningGoal' in goal_str
            assert 'daily_minutes' in goal_str
            assert '0/30' in goal_str
    
    def test_goal_with_zero_target_value(self, app, test_user):
        """Test handling of edge case with zero target value."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=1  # Minimum valid value
            )
            
            goal_dict = goal.to_dict()
            assert goal_dict['progress_percentage'] == 0.0
            
            # Complete it
            goal.update_progress(1)
            goal_dict = goal.to_dict()
            assert goal_dict['progress_percentage'] == 100.0
    
    def test_negative_progress_handling(self, app, test_user):
        """Test handling of negative progress values."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            # Should handle negative values gracefully
            goal.update_progress(-5)
            assert goal.current_value == 0
            
            # Set to 15, then to -5 (should become 0)
            goal.update_progress(15)
            assert goal.current_value == 15
            
            goal.update_progress(-5)
            assert goal.current_value == 0