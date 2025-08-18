"""User model for authentication and user management."""
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """User model with authentication and OAuth support."""

    __tablename__ = 'users'

    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User credentials
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)

    # OAuth fields
    oauth_provider = db.Column(db.String(50), nullable=True)
    oauth_id = db.Column(db.String(255), nullable=True)

    # Language preferences (foreign keys as per schema)
    native_language_id = db.Column(db.SmallInteger, db.ForeignKey('languages.id'), nullable=True)
    target_language_id = db.Column(db.SmallInteger, db.ForeignKey('languages.id'), nullable=True)
    
    # Relationships for efficient queries
    native_language = db.relationship('Language', foreign_keys=[native_language_id], lazy='select')
    target_language = db.relationship('Language', foreign_keys=[target_language_id], lazy='select')

    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('oauth_provider', 'oauth_id', name='unique_oauth_user'),
    )

    def set_password(self, password):
        """Hash and set password using Werkzeug security."""
        if password:
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Debug representation of User model."""
        return f'<User {self.id}: {self.email}>'

    def to_dict(self, include_languages=False):
        """Convert User model to dictionary for JSON serialization."""
        user_dict = {
            'id': self.id,
            'email': self.email,
            'oauth_provider': self.oauth_provider,
            'native_language_id': self.native_language_id,
            'target_language_id': self.target_language_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_languages:
            user_dict['native_language'] = self.native_language.to_dict() if self.native_language else None
            user_dict['target_language'] = self.target_language.to_dict() if self.target_language else None
            
        return user_dict
