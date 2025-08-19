"""Language model for storing available languages with display information and language codes."""
from app import db


class Language(db.Model):
    """Language model for available language options."""

    __tablename__ = 'languages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    display_name = db.Column(db.Text, nullable=False)
    code = db.Column(db.Text, nullable=False, unique=True)

    def to_dict(self):
        """Convert Language instance to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'code': self.code
        }

    def __repr__(self):
        return f'<Language {self.name}>'
