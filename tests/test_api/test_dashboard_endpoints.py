"""Tests for dashboard API endpoints."""
import pytest
import json
from datetime import date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.learning_goal import LearningGoal
from app.models.subtitle import UserProgress, SubLink


@pytest.fixture
def app():
    """Create test app instance."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
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
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client."""
    # Login the test user
    with client.session_transaction() as sess:
        sess['user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client


class TestDashboardEndpoints:
    """Test dashboard API endpoints."""
    
    def test_dashboard_stats_unauthenticated(self, client):
        """Test dashboard stats endpoint without authentication."""
        response = client.get('/api/progress/dashboard')
        assert response.status_code == 401
    
    def test_dashboard_stats_no_data(self, authenticated_client):
        """Test dashboard stats with no user data."""
        response = authenticated_client.get('/api/progress/dashboard')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'stats' in data
        
        stats = data['stats']
        assert stats['total_study_minutes'] == 0
        assert stats['movies_completed'] == 0
        assert stats['total_alignments'] == 0
        assert stats['current_streak'] == 0
    
    def test_progress_charts_unauthenticated(self, client):
        """Test progress charts endpoint without authentication."""
        response = client.get('/api/progress/charts')
        assert response.status_code == 401
    
    def test_progress_charts_default_params(self, authenticated_client):
        """Test progress charts with default parameters."""
        response = authenticated_client.get('/api/progress/charts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'chart_data' in data
        assert 'period' in data
        assert 'days' in data
        assert data['period'] == 'weekly'
        assert data['days'] == 30
        
        # Check chart data structure
        chart_data = data['chart_data']
        assert 'labels' in chart_data
        assert 'datasets' in chart_data
    
    def test_progress_charts_custom_params(self, authenticated_client):
        """Test progress charts with custom parameters."""
        response = authenticated_client.get('/api/progress/charts?period=monthly&days=60')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['period'] == 'monthly'
        assert data['days'] == 60
    
    def test_progress_charts_invalid_params(self, authenticated_client):
        """Test progress charts with invalid parameters."""
        # Invalid period should default to weekly
        response = authenticated_client.get('/api/progress/charts?period=invalid&days=-10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['period'] == 'weekly'
        assert data['days'] == 30  # Should default to 30 for negative value
    
    def test_progress_charts_max_days_limit(self, authenticated_client):
        """Test progress charts respects maximum days limit."""
        response = authenticated_client.get('/api/progress/charts?days=500')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['days'] == 365  # Should be capped at 365
    
    def test_learning_streak_unauthenticated(self, client):
        """Test learning streak endpoint without authentication."""
        response = client.get('/api/progress/streak')
        assert response.status_code == 401
    
    def test_learning_streak_no_data(self, authenticated_client):
        """Test learning streak with no data."""
        response = authenticated_client.get('/api/progress/streak')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'streak' in data
        
        streak = data['streak']
        assert streak['current_streak'] == 0
        assert streak['longest_streak'] == 0
        assert streak['last_activity_date'] is None
    
    def test_session_history_unauthenticated(self, client):
        """Test session history endpoint without authentication."""
        response = client.get('/api/progress/session-history')
        assert response.status_code == 401
    
    def test_session_history_default_params(self, authenticated_client):
        """Test session history with default parameters."""
        response = authenticated_client.get('/api/progress/session-history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'session_history' in data
        assert 'limit' in data
        assert 'days' in data
        assert data['limit'] == 50
        assert data['days'] == 30
        assert isinstance(data['session_history'], list)
    
    def test_session_history_custom_params(self, authenticated_client):
        """Test session history with custom parameters."""
        response = authenticated_client.get('/api/progress/session-history?limit=10&days=7')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['limit'] == 10
        assert data['days'] == 7
    
    def test_session_history_param_limits(self, authenticated_client):
        """Test session history parameter limits."""
        # Test maximum limit
        response = authenticated_client.get('/api/progress/session-history?limit=200&days=500')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['limit'] == 100  # Should be capped at 100
        assert data['days'] == 365   # Should be capped at 365
        
        # Test minimum values
        response = authenticated_client.get('/api/progress/session-history?limit=-5&days=-10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['limit'] == 50  # Should default to 50
        assert data['days'] == 30   # Should default to 30


class TestGoalsEndpoints:
    """Test learning goals API endpoints."""
    
    def test_create_goal_unauthenticated(self, client):
        """Test creating goal without authentication."""
        response = client.post('/api/goals', json={
            'goal_type': 'daily_minutes',
            'target_value': 30
        })
        assert response.status_code == 401
    
    def test_create_goal_success(self, authenticated_client):
        """Test successful goal creation."""
        goal_data = {
            'goal_type': 'daily_minutes',
            'target_value': 30,
            'deadline': '2024-12-31'
        }
        
        response = authenticated_client.post('/api/goals', json=goal_data)
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'goal' in data
        assert data['goal']['goal_type'] == 'daily_minutes'
        assert data['goal']['target_value'] == 30
    
    def test_create_goal_missing_data(self, authenticated_client):
        """Test creating goal with missing data."""
        # Missing goal_type
        response = authenticated_client.post('/api/goals', json={
            'target_value': 30
        })
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'goal_type is required' in data['error']
        
        # Missing target_value
        response = authenticated_client.post('/api/goals', json={
            'goal_type': 'daily_minutes'
        })
        assert response.status_code == 400
    
    def test_create_goal_invalid_json(self, authenticated_client):
        """Test creating goal with invalid JSON."""
        response = authenticated_client.post('/api/goals', data='invalid json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'Invalid JSON data' in data['error']
    
    def test_get_goals_unauthenticated(self, client):
        """Test getting goals without authentication."""
        response = client.get('/api/goals')
        assert response.status_code == 401
    
    def test_get_goals_empty(self, authenticated_client):
        """Test getting goals when user has none."""
        response = authenticated_client.get('/api/goals')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'goals' in data
        assert 'count' in data
        assert data['count'] == 0
        assert data['goals'] == []
    
    def test_get_goals_with_data(self, app, authenticated_client, test_user):
        """Test getting goals when user has goals."""
        with app.app_context():
            # Create test goals
            goal1 = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            goal2 = LearningGoal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100
            )
            
            db.session.add(goal1)
            db.session.add(goal2)
            db.session.commit()
        
        response = authenticated_client.get('/api/goals')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['count'] == 2
        assert len(data['goals']) == 2
    
    def test_get_goals_active_only_param(self, app, authenticated_client, test_user):
        """Test getting goals with active_only parameter."""
        with app.app_context():
            # Create active and inactive goals
            active_goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            inactive_goal = LearningGoal(
                user_id=test_user.id,
                goal_type='weekly_alignments',
                target_value=100
            )
            inactive_goal.is_active = False
            
            db.session.add(active_goal)
            db.session.add(inactive_goal)
            db.session.commit()
        
        # Test active_only=true (default)
        response = authenticated_client.get('/api/goals')
        data = json.loads(response.data)
        assert data['count'] == 1
        
        # Test active_only=false
        response = authenticated_client.get('/api/goals?active_only=false')
        data = json.loads(response.data)
        assert data['count'] == 2
    
    def test_update_goal_unauthenticated(self, client):
        """Test updating goal without authentication."""
        response = client.put('/api/goals/1', json={'target_value': 60})
        assert response.status_code == 401
    
    def test_update_goal_success(self, app, authenticated_client, test_user):
        """Test successful goal update."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            db.session.add(goal)
            db.session.commit()
            goal_id = goal.id
        
        update_data = {
            'target_value': 60,
            'deadline': '2024-12-31'
        }
        
        response = authenticated_client.put(f'/api/goals/{goal_id}', json=update_data)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert data['goal']['target_value'] == 60
    
    def test_update_nonexistent_goal(self, authenticated_client):
        """Test updating non-existent goal."""
        response = authenticated_client.put('/api/goals/99999', json={'target_value': 60})
        assert response.status_code == 400
    
    def test_delete_goal_unauthenticated(self, client):
        """Test deleting goal without authentication."""
        response = client.delete('/api/goals/1')
        assert response.status_code == 401
    
    def test_delete_goal_success(self, app, authenticated_client, test_user):
        """Test successful goal deletion."""
        with app.app_context():
            goal = LearningGoal(
                user_id=test_user.id,
                goal_type='daily_minutes',
                target_value=30
            )
            db.session.add(goal)
            db.session.commit()
            goal_id = goal.id
        
        response = authenticated_client.delete(f'/api/goals/{goal_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        
        # Verify goal is deleted
        response = authenticated_client.get('/api/goals')
        data = json.loads(response.data)
        assert data['count'] == 0
    
    def test_delete_nonexistent_goal(self, authenticated_client):
        """Test deleting non-existent goal."""
        response = authenticated_client.delete('/api/goals/99999')
        assert response.status_code == 400
    
    def test_goal_validation_errors(self, authenticated_client):
        """Test various goal validation errors."""
        # Invalid goal_type
        response = authenticated_client.post('/api/goals', json={
            'goal_type': 'invalid_type',
            'target_value': 30
        })
        assert response.status_code == 400
        
        # Invalid target_value
        response = authenticated_client.post('/api/goals', json={
            'goal_type': 'daily_minutes',
            'target_value': -10
        })
        assert response.status_code == 400
        
        # Invalid deadline format
        response = authenticated_client.post('/api/goals', json={
            'goal_type': 'daily_minutes',
            'target_value': 30,
            'deadline': 'invalid-date'
        })
        assert response.status_code == 400
    
    def test_create_goal_all_types(self, authenticated_client):
        """Test creating goals of all valid types."""
        valid_types = ['daily_minutes', 'weekly_alignments', 'movie_completion']
        
        for goal_type in valid_types:
            goal_data = {
                'goal_type': goal_type,
                'target_value': 10
            }
            
            response = authenticated_client.post('/api/goals', json=goal_data)
            assert response.status_code == 201
            
            data = json.loads(response.data)
            assert data['goal']['goal_type'] == goal_type
    
    def test_goal_deadline_validation(self, authenticated_client):
        """Test goal deadline validation."""
        # Past deadline should fail
        past_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = authenticated_client.post('/api/goals', json={
            'goal_type': 'daily_minutes',
            'target_value': 30,
            'deadline': past_date
        })
        assert response.status_code == 400
        
        # Future deadline should succeed
        future_date = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        response = authenticated_client.post('/api/goals', json={
            'goal_type': 'daily_minutes',
            'target_value': 30,
            'deadline': future_date
        })
        assert response.status_code == 201