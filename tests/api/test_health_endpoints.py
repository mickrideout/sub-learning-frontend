"""Test cases for health check API endpoints."""
import json
from unittest.mock import patch

from app.models.user import User
from app import db


class TestHealthEndpoints:
    """Test cases for health check endpoints."""

    def test_index_endpoint(self, client):
        """Test the index endpoint."""
        response = client.get('/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["message"] == "Sub Learning Application"
        assert data["status"] == "running"
        assert "health" in data["endpoints"]
        assert "database_health" in data["endpoints"]

    def test_health_endpoint(self, client, app):
        """Test the main health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "python_version" in data
        assert "system" in data
        assert "database" in data

        # Check database section
        db_data = data["database"]
        assert db_data["status"] == "connected"
        assert db_data["engine"] == "sqlite"
        assert "tables" in db_data
        assert "users" in db_data["tables"]

    def test_health_endpoint_with_users(self, client, app):
        """Test health endpoint with user data."""
        with app.app_context():
            # Create test users
            user1 = User(email="test1@example.com")
            user2 = User(email="test2@example.com")
            db.session.add_all([user1, user2])
            db.session.commit()

        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        db_data = data["database"]
        assert db_data["tables"]["users"]["count"] == 2
        assert db_data["tables"]["users"]["exists"] is True

    def test_database_health_endpoint(self, client):
        """Test the dedicated database health endpoint."""
        response = client.get('/health/database')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "connected"
        assert data["engine"] == "sqlite"
        assert "timestamp" in data
        assert "tables" in data
        assert "total_tables" in data

        # Check users table info
        assert data["tables"]["users"]["exists"] is True
        assert data["tables"]["users"]["count"] == 0  # No users initially

    def test_database_health_endpoint_with_data(self, client, app):
        """Test database health endpoint with test data."""
        with app.app_context():
            # Create test user
            user = User(email="health@example.com")
            db.session.add(user)
            db.session.commit()

        response = client.get('/health/database')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["tables"]["users"]["count"] == 1

    def test_health_endpoint_database_error(self, client, app):
        """Test health endpoint when database is down."""
        with patch('app.blueprints.main.routes.get_database_status') as mock_db_status:
            mock_db_status.return_value = (
                {"status": "disconnected", "error": "Connection failed"},
                False
            )

            response = client.get('/health')
            assert response.status_code == 503  # Service Unavailable

            data = json.loads(response.data)
            assert data["status"] == "unhealthy"
            assert data["database"]["status"] == "disconnected"

    def test_database_health_endpoint_error(self, client):
        """Test database health endpoint with connection error."""
        with patch('app.blueprints.main.routes.get_database_status') as mock_db_status:
            mock_db_status.return_value = (
                {"status": "disconnected", "error": "Database unavailable"},
                False
            )

            response = client.get('/health/database')
            assert response.status_code == 503

            data = json.loads(response.data)
            assert data["status"] == "disconnected"
            assert data["error"] == "Database unavailable"

    def test_health_endpoint_exception(self, client):
        """Test health endpoint with unexpected exception."""
        with patch('app.blueprints.main.routes.get_database_status') as mock_db_status:
            mock_db_status.side_effect = Exception("Unexpected error")

            response = client.get('/health')
            assert response.status_code == 500

            data = json.loads(response.data)
            assert data["error"] == "Health check failed"
            assert data["code"] == "health_check_error"

    def test_database_health_endpoint_exception(self, client):
        """Test database health endpoint with unexpected exception."""
        with patch('app.blueprints.main.routes.get_database_status') as mock_db_status:
            mock_db_status.side_effect = Exception("Database error")

            response = client.get('/health/database')
            assert response.status_code == 500

            data = json.loads(response.data)
            assert data["status"] == "error"
            assert data["error"] == "Database health check failed"
            assert data["code"] == "database_health_error"
