"""Test cases for database utility functions."""
import pytest
from unittest.mock import patch

from app import db
from app.models.user import User
from app.utils.database import (
    test_database_connection,
    get_database_info,
    database_transaction,
    safe_execute_query,
    check_table_exists,
    get_table_row_count
)


def test_database_connection_function(app):
    """Test database connection outside of class (requires app context)."""
    with app.app_context():
        success, error = test_database_connection()
        assert success is True
        assert error is None


class TestDatabaseUtils:
    """Test cases for database utility functions."""

    def test_test_database_connection_success(self, app):
        """Test successful database connection test."""
        with app.app_context():
            success, error = test_database_connection()
            assert success is True
            assert error is None

    def test_test_database_connection_failure(self, app):
        """Test database connection failure."""
        with app.app_context():
            with patch('app.db.engine.connect') as mock_connect:
                mock_connect.side_effect = Exception("Connection failed")

                success, error = test_database_connection()
                assert success is False
                assert "Connection failed" in error

    def test_get_database_info(self, app):
        """Test get_database_info function."""
        with app.app_context():
            # Create a test user
            user = User(email="test@example.com")
            db.session.add(user)
            db.session.commit()

            info = get_database_info()

            assert info["engine_type"] == "sqlite"
            assert info["connection_status"] == "connected"
            assert isinstance(info["tables"], list)
            assert len(info["tables"]) > 0

            # Check if users table info is present
            users_table = next((t for t in info["tables"] if t["name"] == "users"), None)
            assert users_table is not None
            assert users_table["row_count"] == 1
            assert "email" in users_table["columns"]

    def test_database_transaction_success(self, app):
        """Test successful database transaction."""
        with app.app_context():
            with database_transaction():
                user = User(email="test@example.com")
                db.session.add(user)

            # User should be committed
            assert User.query.filter_by(email="test@example.com").first() is not None

    def test_database_transaction_rollback(self, app):
        """Test database transaction rollback on error."""
        with app.app_context():
            with pytest.raises(Exception):
                with database_transaction():
                    user = User(email="test@example.com")
                    db.session.add(user)
                    raise Exception("Test error")

            # User should not exist due to rollback
            assert User.query.filter_by(email="test@example.com").first() is None

    def test_safe_execute_query_select(self, app):
        """Test safe query execution for SELECT queries."""
        with app.app_context():
            # Create test data
            user = User(email="test@example.com")
            db.session.add(user)
            db.session.commit()

            success, result = safe_execute_query("SELECT email FROM users WHERE email = :email",
                                                 {"email": "test@example.com"})

            assert success is True
            assert len(result) == 1
            assert result[0][0] == "test@example.com"

    def test_safe_execute_query_invalid(self, app):
        """Test safe query execution with invalid query."""
        with app.app_context():
            success, result = safe_execute_query("INVALID QUERY")

            assert success is False
            assert "Database query failed" in result

    def test_check_table_exists(self, app):
        """Test table existence checking."""
        with app.app_context():
            assert check_table_exists("users") is True
            assert check_table_exists("nonexistent_table") is False

    def test_get_table_row_count(self, app):
        """Test table row count functionality."""
        with app.app_context():
            # Initially no users
            assert get_table_row_count("users") == 0

            # Add a user
            user = User(email="test@example.com")
            db.session.add(user)
            db.session.commit()

            # Should have one user
            assert get_table_row_count("users") == 1

            # Nonexistent table
            assert get_table_row_count("nonexistent_table") is None

    def test_get_database_info_connection_error(self, app):
        """Test get_database_info with connection error."""
        with app.app_context():
            with patch('app.utils.database.test_database_connection') as mock_test:
                mock_test.return_value = (False, "Connection failed")

                info = get_database_info()

                assert info["connection_status"] == "disconnected"
                assert "connection_error" in info
