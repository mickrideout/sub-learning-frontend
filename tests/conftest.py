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
        
        # Add sample data for testing
        from app.models import Language, SubTitle, SubLink
        
        # Create sample languages
        languages = [
            Language(id=1, name='english', display_name='English', code='en'),
            Language(id=2, name='spanish', display_name='Spanish', code='es'),
            Language(id=3, name='french', display_name='French', code='fr'),
            Language(id=4, name='german', display_name='German', code='de'),
            Language(id=5, name='italian', display_name='Italian', code='it'),
        ]
        for lang in languages:
            database.session.merge(lang)
        
        # Create sample movies
        movies = [
            SubTitle(id=1, title='The Matrix'),
            SubTitle(id=2, title='Inception'),
            SubTitle(id=3, title='Pulp Fiction'),
            SubTitle(id=4, title='The Godfather'),
            SubTitle(id=5, title='Casablanca'),
        ]
        for movie in movies:
            database.session.merge(movie)
        
        # Create sample subtitle links
        links = [
            SubLink(id=1, fromid=1, fromlang=1, toid=1, tolang=2),  # Matrix EN->ES
            SubLink(id=2, fromid=1, fromlang=1, toid=1, tolang=3),  # Matrix EN->FR
            SubLink(id=3, fromid=2, fromlang=1, toid=2, tolang=2),  # Inception EN->ES
            SubLink(id=4, fromid=3, fromlang=1, toid=3, tolang=2),  # Pulp Fiction EN->ES
            SubLink(id=5, fromid=4, fromlang=1, toid=4, tolang=5),  # Godfather EN->IT
        ]
        for link in links:
            database.session.merge(link)
        
        database.session.commit()
        
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
def auth_user(app, client):
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
