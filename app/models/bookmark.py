"""Bookmark model for user subtitle learning bookmarks."""
from app import db


class Bookmark(db.Model):
    """Bookmark model for saving specific subtitle alignments for focused review."""
    
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sub_link_id = db.Column(db.Integer, db.ForeignKey('sub_links.id'), nullable=False)
    alignment_index = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='bookmarks')
    sub_link = db.relationship('SubLink', backref='bookmarks')
    
    # Unique constraint to prevent duplicate bookmarks
    __table_args__ = (
        db.UniqueConstraint('user_id', 'sub_link_id', 'alignment_index'),
        db.Index('idx_bookmarks_user', 'user_id'),
        db.Index('idx_bookmarks_link', 'sub_link_id'),
        db.Index('idx_bookmarks_active', 'user_id', 'is_active')
    )
    
    def to_dict(self):
        """Convert Bookmark to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sub_link_id': self.sub_link_id,
            'alignment_index': self.alignment_index,
            'note': self.note,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Bookmark {self.id}: User {self.user_id}, SubLink {self.sub_link_id}, Index {self.alignment_index}>'