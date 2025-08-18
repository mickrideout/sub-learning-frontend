"""Authentication service layer with business logic."""
import secrets
from datetime import datetime
from flask import current_app
from app import db
from app.models import User


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""
    pass


class AuthService:
    """Authentication business logic service."""

    @staticmethod
    def register_user(email, password, native_language_id=None,
                      target_language_id=None):
        """
        Register a new user with email and password.

        Args:
            email (str): User's email address
            password (str): User's plain text password
            native_language_id (int, optional): User's native language ID
            target_language_id (int, optional): User's target language ID

        Returns:
            User: The created user object

        Raises:
            AuthenticationError: If email is already registered or validation fails
        """
        email = email.lower().strip()

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise AuthenticationError('Email address already registered')

        try:
            # Create new user
            user = User(
                email=email,
                native_language_id=native_language_id,
                target_language_id=target_language_id,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            user.set_password(password)

            # Save to database
            db.session.add(user)
            db.session.commit()

            current_app.logger.info(f'New user registered: {email}')
            return user

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f'User registration failed for {email}: {str(e)}'
            )
            raise AuthenticationError(f'Registration failed: {str(e)}')

    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user with email and password.

        Args:
            email (str): User's email address
            password (str): User's plain text password

        Returns:
            User: The authenticated user object

        Raises:
            AuthenticationError: If authentication fails
        """
        email = email.lower().strip()

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            current_app.logger.warning(
                f'Login attempt with non-existent email: {email}'
            )
            raise AuthenticationError('Invalid email or password')

        if not user.is_active:
            current_app.logger.warning(f'Login attempt for inactive user: {email}')
            raise AuthenticationError('Account is deactivated')

        # Check password
        if not user.check_password(password):
            current_app.logger.warning(f'Failed login attempt for user: {email}')
            raise AuthenticationError('Invalid email or password')

        current_app.logger.info(f'Successful login for user: {email}')
        return user

    @staticmethod
    def generate_password_reset_token():
        """
        Generate a secure password reset token.

        Returns:
            str: A secure random token for password reset
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_password_reset_token(token, expiry_hours=24):
        """
        Validate a password reset token (basic implementation).

        Note: This is a basic implementation. In production, tokens should be
        stored in the database with expiration timestamps.

        Args:
            token (str): The password reset token
            expiry_hours (int): Token expiry time in hours

        Returns:
            bool: True if token is valid (basic validation)
        """
        # Basic token format validation
        if not token or len(token) < 32:
            return False

        # In a full implementation, we would:
        # 1. Store tokens in database with user_id and expiry
        # 2. Check if token exists and hasn't expired
        # 3. Mark token as used after successful reset

        return True

    @staticmethod
    def reset_password(email, new_password):
        """
        Reset user password.

        Args:
            email (str): User's email address
            new_password (str): New password to set

        Returns:
            bool: True if password was reset successfully

        Raises:
            AuthenticationError: If user not found or reset fails
        """
        email = email.lower().strip()

        user = User.query.filter_by(email=email).first()
        if not user:
            raise AuthenticationError('User not found')

        try:
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()

            current_app.logger.info(f'Password reset successful for user: {email}')
            return True

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f'Password reset failed for {email}: {str(e)}'
            )
            raise AuthenticationError(f'Password reset failed: {str(e)}')

    @staticmethod
    def deactivate_user(user_id):
        """
        Deactivate a user account.

        Args:
            user_id (int): User ID to deactivate

        Returns:
            bool: True if user was deactivated successfully

        Raises:
            AuthenticationError: If user not found or deactivation fails
        """
        user = User.query.get(user_id)
        if not user:
            raise AuthenticationError('User not found')

        try:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.session.commit()

            current_app.logger.info(f'User deactivated: {user.email}')
            return True

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f'User deactivation failed for {user_id}: {str(e)}'
            )
            raise AuthenticationError(f'User deactivation failed: {str(e)}')
