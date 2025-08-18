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