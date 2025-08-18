"""Test cases for User model."""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.user import User


class TestUserModel:
    """Test cases for User model functionality."""

    def test_user_creation(self, app):
        """Test basic user creation."""
        with app.app_context():
            user = User(
                email="test@example.com",
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.email == "test@example.com"
            assert user.is_active is True
            assert user.password_hash is None
            assert user.oauth_provider is None
            assert user.oauth_id is None
            assert isinstance(user.created_at, datetime)
            assert isinstance(user.updated_at, datetime)

    def test_user_password_hashing(self, app):
        """Test password hashing functionality."""
        with app.app_context():
            user = User(email="test@example.com")
            user.set_password("testpassword123")

            # Password should be hashed
            assert user.password_hash is not None
            assert user.password_hash != "testpassword123"

            # Should be able to check correct password
            assert user.check_password("testpassword123") is True
            assert user.check_password("wrongpassword") is False

    def test_user_password_none(self, app):
        """Test user without password."""
        with app.app_context():
            user = User(email="oauth@example.com")

            # No password set
            assert user.password_hash is None
            assert user.check_password("anypassword") is False

    def test_user_email_uniqueness(self, app):
        """Test email uniqueness constraint."""
        with app.app_context():
            user1 = User(email="test@example.com")
            user2 = User(email="test@example.com")

            db.session.add(user1)
            db.session.commit()

            db.session.add(user2)

            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_oauth_user_creation(self, app):
        """Test OAuth user creation."""
        with app.app_context():
            user = User(
                email="oauth@example.com",
                oauth_provider="google",
                oauth_id="12345",
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

            assert user.oauth_provider == "google"
            assert user.oauth_id == "12345"
            assert user.password_hash is None

    def test_oauth_unique_constraint(self, app):
        """Test OAuth provider/ID uniqueness."""
        with app.app_context():
            user1 = User(
                email="user1@example.com",
                oauth_provider="google",
                oauth_id="12345"
            )
            user2 = User(
                email="user2@example.com",
                oauth_provider="google",
                oauth_id="12345"
            )

            db.session.add(user1)
            db.session.commit()

            db.session.add(user2)

            with pytest.raises(IntegrityError):
                db.session.commit()

    def test_user_repr(self, app):
        """Test User string representation."""
        with app.app_context():
            user = User(email="test@example.com")
            db.session.add(user)
            db.session.commit()

            repr_str = repr(user)
            assert f"<User {user.id}: test@example.com>" == repr_str

    def test_user_to_dict(self, app):
        """Test User to dictionary conversion."""
        with app.app_context():
            user = User(
                email="test@example.com",
                oauth_provider="google",
                oauth_id="12345",
                native_language_id=1,
                target_language_id=2,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

            user_dict = user.to_dict()

            expected_keys = {
                'id', 'email', 'oauth_provider', 'native_language_id',
                'target_language_id', 'is_active', 'created_at', 'updated_at'
            }
            assert set(user_dict.keys()) == expected_keys

            assert user_dict['id'] == user.id
            assert user_dict['email'] == "test@example.com"
            assert user_dict['oauth_provider'] == "google"
            assert user_dict['native_language_id'] == 1
            assert user_dict['target_language_id'] == 2
            assert user_dict['is_active'] is True

            # Check datetime serialization
            assert isinstance(user_dict['created_at'], str)
            assert isinstance(user_dict['updated_at'], str)

    def test_user_defaults(self, app):
        """Test User model default values."""
        with app.app_context():
            user = User(email="test@example.com")
            db.session.add(user)
            db.session.commit()

            # Default values
            assert user.is_active is True
            assert user.password_hash is None
            assert user.oauth_provider is None
            assert user.oauth_id is None
            assert user.native_language_id is None
            assert user.target_language_id is None

            # Timestamps should be set
            assert user.created_at is not None
            assert user.updated_at is not None

    def test_user_updated_at(self, app):
        """Test that updated_at is modified on update."""
        with app.app_context():
            user = User(email="test@example.com")
            db.session.add(user)
            db.session.commit()

            original_updated = user.updated_at

            # Update the user
            user.email = "updated@example.com"
            db.session.commit()

            # updated_at should have changed
            assert user.updated_at > original_updated
