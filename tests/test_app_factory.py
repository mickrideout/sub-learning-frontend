"""Test Flask app factory."""
import pytest
from app import create_app


def test_config():
    """Test app configuration."""
    assert not create_app().testing
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    }
    assert create_app(test_config).testing


def test_app_creation():
    """Test Flask app creation."""
    app = create_app()
    assert app is not None
    assert app.config['SECRET_KEY'] is not None
