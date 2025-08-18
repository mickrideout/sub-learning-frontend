"""Pytest configuration and fixtures."""
import pytest
from app import create_app
from app import db as database
from app.models.user import User
from flask_login import login_user


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


@pytest.fixture
def authenticated_user(app, client):
    """Create and authenticate a test user."""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('password123')
        database.session.add(user)
        database.session.commit()
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        return user
