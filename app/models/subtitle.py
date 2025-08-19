"""Subtitle models for movie content management."""
from app import db


class SubTitle(db.Model):
    """Movie title model for subtitle catalog."""
    
    __tablename__ = 'sub_titles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        """Convert SubTitle to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title
        }
    
    def __repr__(self):
        return f'<SubTitle {self.id}: {self.title}>'


class SubLine(db.Model):
    """Subtitle line model for storing individual subtitle content."""
    
    __tablename__ = 'sub_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('sub_titles.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'), nullable=False)
    
    # Relationships
    movie = db.relationship('SubTitle', backref='subtitle_lines')
    language = db.relationship('Language', backref='subtitle_lines')
    
    def to_dict(self):
        """Convert SubLine to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'sequence': self.sequence,
            'content': self.content,
            'language_id': self.language_id
        }
    
    def __repr__(self):
        return f'<SubLine {self.id}: Movie {self.movie_id}, Seq {self.sequence}>'


class SubLink(db.Model):
    """Translation link model representing subtitle availability between languages."""
    
    __tablename__ = 'sub_links'
    
    id = db.Column(db.Integer, primary_key=True)
    fromid = db.Column(db.Integer, db.ForeignKey('sub_titles.id'), nullable=False)
    fromlang = db.Column(db.SmallInteger, db.ForeignKey('languages.id'), nullable=False)
    toid = db.Column(db.Integer, db.ForeignKey('sub_titles.id'), nullable=False)
    tolang = db.Column(db.SmallInteger, db.ForeignKey('languages.id'), nullable=False)
    
    # Relationships
    from_subtitle = db.relationship('SubTitle', foreign_keys=[fromid], backref='from_links')
    to_subtitle = db.relationship('SubTitle', foreign_keys=[toid], backref='to_links')
    from_language = db.relationship('Language', foreign_keys=[fromlang], backref='from_sub_links')
    to_language = db.relationship('Language', foreign_keys=[tolang], backref='to_sub_links')
    
    def to_dict(self):
        """Convert SubLink to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'fromid': self.fromid,
            'fromlang': self.fromlang,
            'toid': self.toid,
            'tolang': self.tolang
        }
    
    def __repr__(self):
        return f'<SubLink {self.id}: {self.fromid}({self.fromlang}) -> {self.toid}({self.tolang})>'


class SubLinkLine(db.Model):
    """Alignment data model linking subtitle lines between languages."""
    
    __tablename__ = 'sub_link_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    sub_link_id = db.Column(db.Integer, db.ForeignKey('sub_links.id'), nullable=False)
    link_data = db.Column(db.JSON, nullable=False)  # Array of aligned line pairs [[source_line_ids], [target_line_ids]]
    
    # Relationship
    sub_link = db.relationship('SubLink', backref='alignment_data')
    
    def to_dict(self):
        """Convert SubLinkLine to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'sub_link_id': self.sub_link_id,
            'link_data': self.link_data
        }
    
    def __repr__(self):
        return f'<SubLinkLine {self.id}: SubLink {self.sub_link_id}>'


class UserProgress(db.Model):
    """User progress tracking model for subtitle learning sessions."""
    
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sub_link_id = db.Column(db.Integer, db.ForeignKey('sub_links.id'), nullable=False)
    current_alignment_index = db.Column(db.Integer, default=0, nullable=False)
    last_accessed = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='progress_sessions')
    sub_link = db.relationship('SubLink', backref='user_sessions')
    
    def to_dict(self):
        """Convert UserProgress to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sub_link_id': self.sub_link_id,
            'current_alignment_index': self.current_alignment_index,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }
    
    def __repr__(self):
        return f'<UserProgress {self.id}: User {self.user_id}, SubLink {self.sub_link_id}>'