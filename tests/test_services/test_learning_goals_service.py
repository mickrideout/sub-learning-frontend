"""Tests for LearningGoalsService."""
import pytest
from datetime import date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.learning_goal import LearningGoal
from app.services.learning_goals_service import LearningGoalsService, LearningGoalsServiceError


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


class TestLearningGoalsService:
    """Test LearningGoalsService functionality."""
    
    def test_create_goal_success(self, app, test_user):
        """Test successful goal creation."""
        with app.app_context():
            goal_data = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30,
                deadline='2024-12-31'
            )
            
            assert goal_data['user_id'] == test_user.id
            assert goal_data['goal_type'] == 'daily_minutes'
            assert goal_data['target_value'] == 30
            assert goal_data['current_value'] == 0
            assert goal_data['is_active'] is True
            assert goal_data['deadline'] == '2024-12-31'
    
    def test_create_goal_invalid_type(self, app, test_user):
        """Test goal creation with invalid goal type."""
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                LearningGoalsService.create_goal(
                    user_id=test_user.id,
                    goal_type='invalid_type',
                    target_value=30
                )
            
            assert 'Invalid goal_type' in str(exc_info.value)
    
    def test_create_goal_invalid_target_value(self, app, test_user):
        """Test goal creation with invalid target value."""
        with app.app_context():
            # Zero target value
            with pytest.raises(ValueError) as exc_info:
                LearningGoalsService.create_goal(
                    user_id=test_user.id,
                    goal_type='daily_minutes',
                    target_value=0
                )
            assert 'positive integer' in str(exc_info.value)
            
            # Negative target value
            with pytest.raises(ValueError) as exc_info:
                LearningGoalsService.create_goal(
                    user_id=test_user.id,
                    goal_type='daily_minutes',
                    target_value=-10
                )
            assert 'positive integer' in str(exc_info.value)
            
            # Non-integer target value
            with pytest.raises(ValueError) as exc_info:
                LearningGoalsService.create_goal(
                    user_id=test_user.id,
                    goal_type='daily_minutes',
                    target_value='invalid'
                )
            assert 'positive integer' in str(exc_info.value)
    
    def test_create_goal_invalid_deadline(self, app, test_user):
        """Test goal creation with invalid deadline."""
        with app.app_context():
            # Past deadline
            yesterday = date.today() - timedelta(days=1)
            with pytest.raises(ValueError) as exc_info:
                LearningGoalsService.create_goal(
                    user_id=test_user.id,
                    goal_type='daily_minutes',
                    target_value=30,
                    deadline=yesterday.strftime('%Y-%m-%d')
                )
            assert 'must be in the future' in str(exc_info.value)
            
            # Invalid date format
            with pytest.raises(ValueError) as exc_info:
                LearningGoalsService.create_goal(
                    user_id=test_user.id,
                    goal_type='daily_minutes',
                    target_value=30,
                    deadline='invalid-date'
                )
            assert 'YYYY-MM-DD format' in str(exc_info.value)
    
    def test_get_user_goals(self, app, test_user):
        """Test retrieving user goals."""
        with app.app_context():
            # Create test goals
            goal1 = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            goal2 = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100
            )
            
            # Get active goals only (default)
            active_goals = LearningGoalsService.get_user_goals(test_user.id, active_only=True)
            assert len(active_goals) == 2
            
            # Deactivate one goal
            LearningGoalsService.update_goal(test_user.id, goal1['id'], is_active=False)
            
            # Should only get 1 active goal now
            active_goals = LearningGoalsService.get_user_goals(test_user.id, active_only=True)
            assert len(active_goals) == 1
            
            # Get all goals
            all_goals = LearningGoalsService.get_user_goals(test_user.id, active_only=False)
            assert len(all_goals) == 2
    
    def test_get_goal(self, app, test_user):
        """Test retrieving a specific goal."""
        with app.app_context():
            # Create test goal
            goal_data = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='movie_completion',
                target_value=5
            )
            
            # Get the goal
            retrieved_goal = LearningGoalsService.get_goal(test_user.id, goal_data['id'])
            assert retrieved_goal is not None
            assert retrieved_goal['id'] == goal_data['id']
            assert retrieved_goal['goal_type'] == 'movie_completion'
            
            # Try to get non-existent goal
            non_existent = LearningGoalsService.get_goal(test_user.id, 99999)
            assert non_existent is None
    
    def test_update_goal(self, app, test_user):
        """Test updating a goal."""
        with app.app_context():
            # Create test goal
            goal_data = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            # Update target value
            updated_goal = LearningGoalsService.update_goal(
                user_id=test_user.id,
                goal_id=goal_data['id'],
                target_value=60
            )
            
            assert updated_goal['target_value'] == 60
            
            # Update deadline
            future_date = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
            updated_goal = LearningGoalsService.update_goal(
                user_id=test_user.id,
                goal_id=goal_data['id'],
                deadline=future_date
            )
            
            assert updated_goal['deadline'] == future_date
            
            # Update current value
            updated_goal = LearningGoalsService.update_goal(
                user_id=test_user.id,
                goal_id=goal_data['id'],
                current_value=30
            )
            
            assert updated_goal['current_value'] == 30
    
    def test_update_nonexistent_goal(self, app, test_user):
        """Test updating a non-existent goal."""
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                LearningGoalsService.update_goal(
                    user_id=test_user.id,
                    goal_id=99999,
                    target_value=50
                )
            assert 'not found' in str(exc_info.value)
    
    def test_delete_goal(self, app, test_user):
        """Test deleting a goal."""
        with app.app_context():
            # Create test goal
            goal_data = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            # Verify goal exists
            goal = LearningGoalsService.get_goal(test_user.id, goal_data['id'])
            assert goal is not None
            
            # Delete goal
            LearningGoalsService.delete_goal(test_user.id, goal_data['id'])
            
            # Verify goal is deleted
            deleted_goal = LearningGoalsService.get_goal(test_user.id, goal_data['id'])
            assert deleted_goal is None
    
    def test_delete_nonexistent_goal(self, app, test_user):
        """Test deleting a non-existent goal."""
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                LearningGoalsService.delete_goal(test_user.id, 99999)
            assert 'not found' in str(exc_info.value)
    
    def test_update_goal_progress(self, app, test_user):
        """Test updating goal progress for specific type."""
        with app.app_context():
            # Create goals of different types
            daily_goal1 = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            daily_goal2 = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=60
            )
            
            weekly_goal = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100
            )
            
            # Update daily_minutes goals
            updated_goals = LearningGoalsService.update_goal_progress(
                user_id=test_user.id,
                goal_type='daily_minutes',
                progress_amount=15
            )
            
            # Should have updated 2 goals
            assert len(updated_goals) == 2
            
            # Both daily goals should have 15 progress
            for goal in updated_goals:
                assert goal['current_value'] == 15
            
            # Weekly goal should be unaffected
            weekly_goal_check = LearningGoalsService.get_goal(test_user.id, weekly_goal['id'])
            assert weekly_goal_check['current_value'] == 0
    
    def test_check_goal_completion(self, app, test_user):
        """Test checking for goal completion."""
        with app.app_context():
            # Create test goal
            goal_data = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            # Update progress to complete the goal
            LearningGoalsService.update_goal(
                user_id=test_user.id,
                goal_id=goal_data['id'],
                current_value=30
            )
            
            # Check for completions
            achievements = LearningGoalsService.check_goal_completion(test_user.id)
            
            # Should find the completed goal
            assert len(achievements) == 1
            assert achievements[0]['id'] == goal_data['id']
            assert achievements[0]['is_completed'] is True
            
            # Check again - should find no new completions
            achievements = LearningGoalsService.check_goal_completion(test_user.id)
            assert len(achievements) == 0
    
    def test_get_goal_statistics(self, app, test_user):
        """Test getting goal statistics for a user."""
        with app.app_context():
            # Create various goals
            completed_goal = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            
            active_goal = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100
            )
            
            # Past deadline goal (overdue)
            past_deadline = date.today() - timedelta(days=1)
            overdue_goal = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='movie_completion',
                target_value=5,
                deadline=past_deadline.strftime('%Y-%m-%d')
            )
            
            # Complete one goal
            LearningGoalsService.update_goal(
                user_id=test_user.id,
                goal_id=completed_goal['id'],
                current_value=30
            )
            
            # Get statistics
            stats = LearningGoalsService.get_goal_statistics(test_user.id)
            
            assert stats['total_goals'] == 3
            assert stats['completed_goals'] == 1
            assert stats['active_goals'] == 3  # All are still active
            assert stats['completion_rate'] == 33.33  # 1/3 * 100, rounded
            assert stats['overdue_goals'] == 1
            
            # Check goals by type
            assert 'daily_minutes' in stats['goals_by_type']
            assert stats['goals_by_type']['daily_minutes']['total'] == 1
            assert stats['goals_by_type']['daily_minutes']['completed'] == 1
    
    def test_get_goal_statistics_no_goals(self, app, test_user):
        """Test getting statistics when user has no goals."""
        with app.app_context():
            stats = LearningGoalsService.get_goal_statistics(test_user.id)
            
            assert stats['total_goals'] == 0
            assert stats['completed_goals'] == 0
            assert stats['active_goals'] == 0
            assert stats['completion_rate'] == 0.0
            assert stats['overdue_goals'] == 0
            assert stats['goals_by_type'] == {}
    
    def test_create_goal_without_deadline(self, app, test_user):
        """Test creating goal without deadline."""
        with app.app_context():
            goal_data = LearningGoalsService.create_goal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=50
            )
            
            assert goal_data['deadline'] is None
            
            # Verify in database
            goal = LearningGoalsService.get_goal(test_user.id, goal_data['id'])
            assert goal['deadline'] is None
    
    def test_valid_goal_types(self, app, test_user):
        """Test all valid goal types can be created."""
        with app.app_context():
            valid_types = ['daily_minutes', 'weekly_alignments', 'movie_completion']
            
            for goal_type in valid_types:
                goal_data = LearningGoalsService.create_goal(
                    user_id=test_user.id,
                    goal_type=goal_type,
                    target_value=10
                )
                
                assert goal_data['goal_type'] == goal_type
                assert goal_data['target_value'] == 10