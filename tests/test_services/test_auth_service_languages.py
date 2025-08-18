"""Tests for language-related methods in AuthService."""
import pytest
from app.services.auth_service import AuthService, AuthenticationError
from app.models import User, Language
from app import db


class TestAuthServiceLanguages:
    """Test language update functionality in AuthService."""

    def test_update_user_languages_success(self, app):
        """Test successful language update for a user."""
        with app.app_context():
            # Create test user
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            # Create test languages
            english = Language(id=1, name="english", display_name="English", code="en")
            spanish = Language(id=2, name="spanish", display_name="Spanish", code="es")
            db.session.add_all([english, spanish])
            db.session.commit()
            
            # Update user languages
            updated_user = AuthService.update_user_languages(
                user_id=user.id,
                native_language_id=1,
                target_language_id=2
            )
            
            # Verify update
            assert updated_user.native_language_id == 1
            assert updated_user.target_language_id == 2
            assert updated_user.updated_at is not None

    def test_update_user_languages_same_language_error(self, app):
        """Test that updating with same native and target language fails."""
        with app.app_context():
            # Create test user and language
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            english = Language(id=1, name="english", display_name="English", code="en")
            db.session.add(english)
            db.session.commit()
            
            # Attempt to set same language for both
            with pytest.raises(AuthenticationError) as exc_info:
                AuthService.update_user_languages(
                    user_id=user.id,
                    native_language_id=1,
                    target_language_id=1
                )
            
            assert "Native and target languages must be different" in str(exc_info.value)

    def test_update_user_languages_user_not_found(self, app):
        """Test language update with non-existent user."""
        with app.app_context():
            # Create test languages
            english = Language(id=1, name="english", display_name="English", code="en")
            spanish = Language(id=2, name="spanish", display_name="Spanish", code="es")
            db.session.add_all([english, spanish])
            db.session.commit()
            
            # Attempt to update non-existent user
            with pytest.raises(AuthenticationError) as exc_info:
                AuthService.update_user_languages(
                    user_id=999,
                    native_language_id=1,
                    target_language_id=2
                )
            
            assert "User not found" in str(exc_info.value)

    def test_update_user_languages_invalid_native_language(self, app):
        """Test language update with invalid native language ID."""
        with app.app_context():
            # Create test user and one language
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            spanish = Language(id=2, name="spanish", display_name="Spanish", code="es")
            db.session.add(spanish)
            db.session.commit()
            
            # Attempt to update with invalid native language
            with pytest.raises(AuthenticationError) as exc_info:
                AuthService.update_user_languages(
                    user_id=user.id,
                    native_language_id=999,
                    target_language_id=2
                )
            
            assert "Invalid native language" in str(exc_info.value)

    def test_update_user_languages_invalid_target_language(self, app):
        """Test language update with invalid target language ID."""
        with app.app_context():
            # Create test user and one language
            user = User(email="test@example.com", is_active=True)
            user.set_password("testpass")
            db.session.add(user)
            
            english = Language(id=1, name="english", display_name="English", code="en")
            db.session.add(english)
            db.session.commit()
            
            # Attempt to update with invalid target language
            with pytest.raises(AuthenticationError) as exc_info:
                AuthService.update_user_languages(
                    user_id=user.id,
                    native_language_id=1,
                    target_language_id=999
                )
            
            assert "Invalid target language" in str(exc_info.value)