"""Pytest configuration and fixtures."""
import pytest
from app import create_app
from app import db as database


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key"
    })

    with app.app_context():
        database.create_all()
        yield app
        database.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test runner."""
    return app.test_cli_runner()


@pytest.fixture
def db(app):
    """Database fixture for testing."""
    return database
