"""User model for authentication and user management."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
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
    native_language_id = db.Column(db.SmallInteger, nullable=True)
    target_language_id = db.Column(db.SmallInteger, nullable=True)

    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

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

    def to_dict(self):
        """Convert User model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'email': self.email,
            'oauth_provider': self.oauth_provider,
            'native_language_id': self.native_language_id,
            'target_language_id': self.target_language_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
