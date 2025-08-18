"""Authentication forms with validation."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError, Regexp
)
from app.models import User


class RegistrationForm(FlaskForm):
    """User registration form with email validation and password strength."""

    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=255, message='Email must be less than 255 characters')
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128,
               message='Password must be between 8 and 128 characters'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
            message='Password must contain at least one lowercase letter, '
                    'one uppercase letter, and one number'
        )
    ])

    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords must match')
    ])

    submit = SubmitField('Register')

    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError(
                'Email address already registered. Please choose a different one.'
            )


class LoginForm(FlaskForm):
    """User login form with email/password inputs and remember-me option."""

    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])

    remember_me = BooleanField('Remember Me')

    submit = SubmitField('Login')


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form."""

    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        """Check if email exists in the database."""
        user = User.query.filter_by(email=email.data.lower()).first()
        if not user:
            raise ValidationError('No account found with that email address.')


class PasswordResetForm(FlaskForm):
    """Password reset form."""

    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128,
               message='Password must be between 8 and 128 characters'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
            message='Password must contain at least one lowercase letter, '
                    'one uppercase letter, and one number'
        )
    ])

    password_confirm = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords must match')
    ])

    submit = SubmitField('Reset Password')
