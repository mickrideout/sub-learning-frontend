"""Tests for Bookmark model."""
import pytest
from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models.user import User
from app.models.language import Language
from app.models.subtitle import SubTitle, SubLink
from app.models.bookmark import Bookmark


@pytest.fixture
def app():
    """Create test application."""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'GOOGLE_CLIENT_ID': 'test-client-id',
        'GOOGLE_CLIENT_SECRET': 'test-client-secret',
        'FACEBOOK_CLIENT_ID': 'test-facebook-id',
        'FACEBOOK_CLIENT_SECRET': 'test-facebook-secret',
        'APPLE_CLIENT_ID': 'test-apple-id',
        'APPLE_PRIVATE_KEY': 'test-apple-key'
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def sample_data(app):
    """Create sample data for testing."""
    with app.app_context():
        # Create languages
        lang1 = Language(id=1, name='english', display_name='English', code='en')
        lang2 = Language(id=2, name='spanish', display_name='Spanish', code='es')
        db.session.add_all([lang1, lang2])
        
        # Create user
        user = User(
            email='test@example.com',
            password_hash='hashed_password',
            is_active=True,
            email_verified=True,
            native_language_id=lang1.id,
            target_language_id=lang2.id
        )
        db.session.add(user)
        
        # Create subtitles
        subtitle1 = SubTitle(id=1, title='Test Movie 1')
        subtitle2 = SubTitle(id=2, title='Test Movie 2')
        db.session.add_all([subtitle1, subtitle2])
        
        # Create sub_link
        sub_link = SubLink(
            id=1,
            fromid=subtitle1.id,
            fromlang=lang1.id,
            toid=subtitle2.id,
            tolang=lang2.id
        )
        db.session.add(sub_link)
        
        db.session.commit()
        
        return {
            'user': user,
            'sub_link': sub_link,
            'lang1': lang1,
            'lang2': lang2
        }


def test_bookmark_creation(sample_data):
    """Test basic bookmark creation."""
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='Test bookmark note'
    )
    db.session.add(bookmark)
    db.session.commit()
    
    # Verify bookmark was created
    assert bookmark.id is not None
    assert bookmark.user_id == sample_data['user'].id
    assert bookmark.sub_link_id == sample_data['sub_link'].id
    assert bookmark.alignment_index == 0
    assert bookmark.note == 'Test bookmark note'
    assert bookmark.is_active is True
    assert bookmark.created_at is not None


def test_bookmark_without_note(sample_data):
    """Test bookmark creation without note."""
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=5
    )
    db.session.add(bookmark)
    db.session.commit()
    
    assert bookmark.note is None
    assert bookmark.alignment_index == 5


def test_bookmark_unique_constraint(sample_data):
    """Test unique constraint on user_id, sub_link_id, alignment_index."""
    # Create first bookmark
    bookmark1 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=10
    )
    db.session.add(bookmark1)
    db.session.commit()
    
    # Try to create duplicate bookmark
    bookmark2 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=10
    )
    db.session.add(bookmark2)
    
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_bookmark_relationships(sample_data):
    """Test bookmark relationships with user and sub_link."""
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=15
    )
    db.session.add(bookmark)
    db.session.commit()
    
    # Test relationships
    assert bookmark.user == sample_data['user']
    assert bookmark.sub_link == sample_data['sub_link']
    assert bookmark in sample_data['user'].bookmarks
    assert bookmark in sample_data['sub_link'].bookmarks


def test_bookmark_to_dict(sample_data):
    """Test bookmark to_dict method."""
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=20,
        note='Test note for dict conversion'
    )
    db.session.add(bookmark)
    db.session.commit()
    
    bookmark_dict = bookmark.to_dict()
    
    assert isinstance(bookmark_dict, dict)
    assert bookmark_dict['id'] == bookmark.id
    assert bookmark_dict['user_id'] == sample_data['user'].id
    assert bookmark_dict['sub_link_id'] == sample_data['sub_link'].id
    assert bookmark_dict['alignment_index'] == 20
    assert bookmark_dict['note'] == 'Test note for dict conversion'
    assert bookmark_dict['is_active'] is True
    assert 'created_at' in bookmark_dict


def test_bookmark_soft_delete(sample_data):
    """Test soft delete functionality."""
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=25,
        is_active=False
    )
    db.session.add(bookmark)
    db.session.commit()
    
    assert bookmark.is_active is False
    
    # Should be able to create another bookmark with same alignment after soft delete
    bookmark2 = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=25,
        is_active=True
    )
    db.session.add(bookmark2)
    db.session.commit()
    
    assert bookmark2.is_active is True


def test_bookmark_repr(sample_data):
    """Test bookmark __repr__ method."""
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=30
    )
    db.session.add(bookmark)
    db.session.commit()
    
    repr_str = repr(bookmark)
    assert f'<Bookmark {bookmark.id}:' in repr_str
    assert f'User {sample_data["user"].id}' in repr_str
    assert f'SubLink {sample_data["sub_link"].id}' in repr_str
    assert 'Index 30' in repr_str


def test_bookmark_negative_alignment_index(sample_data):
    """Test that negative alignment indices are allowed (validation in service layer)."""
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=-1  # This should be caught by service validation, not model
    )
    db.session.add(bookmark)
    db.session.commit()
    
    # Model allows it, service layer should validate
    assert bookmark.alignment_index == -1


def test_bookmark_long_note(sample_data):
    """Test bookmark with very long note."""
    long_note = 'x' * 2000  # 2000 characters
    
    bookmark = Bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=35,
        note=long_note
    )
    db.session.add(bookmark)
    db.session.commit()
    
    assert len(bookmark.note) == 2000
    assert bookmark.note == long_note