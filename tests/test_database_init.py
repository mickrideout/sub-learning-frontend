"""Integration tests for database initialization script."""
from scripts.init_db import apply_sqlite_optimizations, create_sample_users, main
import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add project root to path to import the script
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDatabaseInitScript:
    """Test cases for database initialization script."""

    def test_apply_sqlite_optimizations(self):
        """Test SQLite optimization application."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            db_path = temp_db.name

        try:
            # Create a basic SQLite database
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()

            # Apply optimizations
            result = apply_sqlite_optimizations(db_path)

            assert result["status"] == "success"
            assert "optimizations" in result

            # Check specific optimizations
            opts = result["optimizations"]
            assert opts["journal_mode"]["success"] is True
            assert opts["journal_mode"]["current"] == "wal"
            assert opts["cache_size"]["success"] is True
            assert opts["temp_store"]["success"] is True

        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_apply_sqlite_optimizations_invalid_path(self):
        """Test optimization with invalid database path."""
        result = apply_sqlite_optimizations("")
        assert "error" in result
        assert result["error"] == "Database path not provided"

    def test_apply_sqlite_optimizations_nonexistent_file(self):
        """Test optimization with nonexistent database file."""
        result = apply_sqlite_optimizations("/nonexistent/path.db")
        assert result["status"] == "error"
        assert "Failed to connect to database" in result["error"]

    def test_create_sample_users(self, app):
        """Test sample user creation."""
        with app.app_context():
            create_sample_users()

            from app.models.user import User

            # Check that sample users were created
            test_user = User.query.filter_by(email="test@example.com").first()
            assert test_user is not None
            assert test_user.check_password("testpassword123") is True
            assert test_user.is_active is True

            oauth_user = User.query.filter_by(email="oauth@example.com").first()
            assert oauth_user is not None
            assert oauth_user.oauth_provider == "google"
            assert oauth_user.oauth_id == "12345"
            assert oauth_user.is_active is True

            inactive_user = User.query.filter_by(email="inactive@example.com").first()
            assert inactive_user is not None
            assert inactive_user.is_active is False

    @patch('scripts.init_db.create_sample_users')
    @patch('scripts.init_db.apply_sqlite_optimizations')
    @patch('sys.argv', ['init_db.py'])
    def test_main_without_samples(self, mock_optimize, mock_samples, app):
        """Test main function without sample data creation."""
        mock_optimize.return_value = {"status": "success"}

        with app.app_context():
            # Mock the app creation to return our test app
            with patch('scripts.init_db.create_app', return_value=app):
                main()

        # Should not create samples
        mock_samples.assert_not_called()
        mock_optimize.assert_called_once()

    @patch('scripts.init_db.create_sample_users')
    @patch('scripts.init_db.apply_sqlite_optimizations')
    @patch('sys.argv', ['init_db.py', '--with-samples'])
    def test_main_with_samples(self, mock_optimize, mock_samples, app):
        """Test main function with sample data creation."""
        mock_optimize.return_value = {"status": "success"}

        with app.app_context():
            # Mock the app creation to return our test app
            with patch('scripts.init_db.create_app', return_value=app):
                main()

        # Should create samples
        mock_samples.assert_called_once()
        mock_optimize.assert_called_once()

    def test_script_executable_permissions(self):
        """Test that the script has executable permissions."""
        script_path = project_root / "scripts" / "init_db.py"
        assert script_path.exists()
        assert os.access(script_path, os.X_OK), "Script should be executable"
