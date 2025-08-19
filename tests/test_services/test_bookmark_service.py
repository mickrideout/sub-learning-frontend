"""Tests for bookmark service business logic."""
import pytest
from datetime import datetime, timedelta, UTC
from app import create_app, db
from app.models.user import User
from app.models.language import Language
from app.models.subtitle import SubTitle, SubLink, SubLinkLine, SubLine
from app.models.bookmark import Bookmark
from app.services.bookmark_service import BookmarkService, BookmarkServiceError


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
        
        # Create subtitle lines
        source_line = SubLine(
            id=101,
            movie_id=subtitle1.id,
            sequence=1,
            content='Hello world',
            language_id=lang1.id
        )
        target_line = SubLine(
            id=102,
            movie_id=subtitle2.id,
            sequence=1,
            content='Hola mundo',
            language_id=lang2.id
        )
        db.session.add_all([source_line, target_line])
        
        # Create alignment data
        sub_link_line = SubLinkLine(
            id=1,
            sub_link_id=sub_link.id,
            link_data=[
                [[101], [102]],  # First alignment pair
                [[101], [102]],  # Second alignment pair
                [[101], [102]]   # Third alignment pair
            ]
        )
        db.session.add(sub_link_line)
        
        db.session.commit()
        
        return {
            'user': user,
            'sub_link': sub_link,
            'sub_link_line': sub_link_line,
            'source_line': source_line,
            'target_line': target_line,
            'lang1': lang1,
            'lang2': lang2
        }


def test_create_bookmark_success(sample_data):
    """Test successful bookmark creation."""
    result = BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='Test bookmark'
    )
    
    assert 'id' in result
    assert result['user_id'] == sample_data['user'].id
    assert result['sub_link_id'] == sample_data['sub_link'].id
    assert result['alignment_index'] == 0
    assert result['note'] == 'Test bookmark'
    assert result['is_active'] is True
    
    # Verify bookmark was actually created in database
    bookmark = Bookmark.query.get(result['id'])
    assert bookmark is not None
    assert bookmark.user_id == sample_data['user'].id


def test_create_bookmark_without_note(sample_data):
    """Test bookmark creation without note."""
    result = BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=1
    )
    
    assert result['note'] is None
    assert result['alignment_index'] == 1


def test_create_bookmark_negative_alignment_index(sample_data):
    """Test bookmark creation with negative alignment index."""
    with pytest.raises(BookmarkServiceError, match="Alignment index cannot be negative"):
        BookmarkService.create_bookmark(
            user_id=sample_data['user'].id,
            sub_link_id=sample_data['sub_link'].id,
            alignment_index=-1
        )


def test_create_bookmark_invalid_sub_link(sample_data):
    """Test bookmark creation with non-existent sub_link."""
    with pytest.raises(BookmarkServiceError, match="Subtitle link 999 not found"):
        BookmarkService.create_bookmark(
            user_id=sample_data['user'].id,
            sub_link_id=999,
            alignment_index=0
        )


def test_create_bookmark_alignment_index_out_of_bounds(sample_data):
    """Test bookmark creation with alignment index exceeding available alignments."""
    with pytest.raises(BookmarkServiceError, match="Alignment index 5 exceeds available alignments"):
        BookmarkService.create_bookmark(
            user_id=sample_data['user'].id,
            sub_link_id=sample_data['sub_link'].id,
            alignment_index=5  # Only 3 alignments available
        )


def test_create_bookmark_duplicate(sample_data):
    """Test duplicate bookmark creation."""
    # Create first bookmark
    BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0
    )
    
    # Try to create duplicate
    with pytest.raises(BookmarkServiceError, match="Bookmark already exists for this alignment"):
        BookmarkService.create_bookmark(
            user_id=sample_data['user'].id,
            sub_link_id=sample_data['sub_link'].id,
            alignment_index=0
        )


def test_create_bookmark_note_too_long(sample_data):
    """Test bookmark creation with note exceeding length limit."""
    long_note = 'x' * 1001  # 1001 characters
    
    with pytest.raises(BookmarkServiceError, match="Bookmark note cannot exceed 1000 characters"):
        BookmarkService.create_bookmark(
            user_id=sample_data['user'].id,
            sub_link_id=sample_data['sub_link'].id,
            alignment_index=0,
            note=long_note
        )


def test_get_user_bookmarks_empty(sample_data):
    """Test getting bookmarks when user has none."""
    result = BookmarkService.get_user_bookmarks(sample_data['user'].id)
    
    assert result['bookmarks'] == []
    assert result['total_count'] == 0
    assert result['has_more'] is False


def test_get_user_bookmarks_with_data(sample_data):
    """Test getting bookmarks with existing data."""
    # Create test bookmarks
    bookmark1 = BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='First bookmark'
    )
    
    bookmark2 = BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=1,
        note='Second bookmark'
    )
    
    result = BookmarkService.get_user_bookmarks(sample_data['user'].id)
    
    assert result['total_count'] == 2
    assert len(result['bookmarks']) == 2
    assert result['has_more'] is False
    
    # Check that bookmarks are returned in descending order by created_at
    assert result['bookmarks'][0]['id'] == bookmark2['id']
    assert result['bookmarks'][1]['id'] == bookmark1['id']


def test_get_user_bookmarks_pagination(sample_data):
    """Test bookmark pagination."""
    # Create multiple bookmarks
    for i in range(5):
        BookmarkService.create_bookmark(
            user_id=sample_data['user'].id,
            sub_link_id=sample_data['sub_link'].id,
            alignment_index=i,
            note=f'Bookmark {i}'
        )
    
    # Test first page
    result = BookmarkService.get_user_bookmarks(
        user_id=sample_data['user'].id,
        limit=3,
        offset=0
    )
    
    assert result['total_count'] == 5
    assert len(result['bookmarks']) == 3
    assert result['has_more'] is True
    
    # Test second page
    result = BookmarkService.get_user_bookmarks(
        user_id=sample_data['user'].id,
        limit=3,
        offset=3
    )
    
    assert len(result['bookmarks']) == 2
    assert result['has_more'] is False


def test_get_user_bookmarks_search(sample_data):
    """Test bookmark search functionality."""
    # Create bookmarks with different notes
    BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='Important grammar rule'
    )
    
    BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=1,
        note='Vocabulary word'
    )
    
    # Search for "grammar"
    result = BookmarkService.get_user_bookmarks(
        user_id=sample_data['user'].id,
        search_query='grammar'
    )
    
    assert result['total_count'] == 1
    assert 'grammar' in result['bookmarks'][0]['note'].lower()


def test_delete_bookmark_success(sample_data):
    """Test successful bookmark deletion."""
    # Create bookmark
    bookmark = BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0
    )
    
    # Delete bookmark
    result = BookmarkService.delete_bookmark(
        user_id=sample_data['user'].id,
        bookmark_id=bookmark['id']
    )
    
    assert result['message'] == 'Bookmark deleted successfully'
    assert result['bookmark_id'] == bookmark['id']
    assert result['remaining_bookmarks'] == 0
    
    # Verify bookmark is soft deleted
    db_bookmark = Bookmark.query.get(bookmark['id'])
    assert db_bookmark.is_active is False


def test_delete_bookmark_not_found(sample_data):
    """Test deleting non-existent bookmark."""
    with pytest.raises(BookmarkServiceError, match="Bookmark not found or already deleted"):
        BookmarkService.delete_bookmark(
            user_id=sample_data['user'].id,
            bookmark_id=999
        )


def test_delete_bookmark_wrong_user(sample_data):
    """Test deleting bookmark owned by different user."""
    # Create another user
    user2 = User(
        email='test2@example.com',
        password_hash='hashed_password',
        is_active=True,
        email_verified=True,
        native_language_id=sample_data['lang1'].id,
        target_language_id=sample_data['lang2'].id
    )
    db.session.add(user2)
    db.session.commit()
    
    # Create bookmark for first user
    bookmark = BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0
    )
    
    # Try to delete with second user
    with pytest.raises(BookmarkServiceError, match="Bookmark not found or already deleted"):
        BookmarkService.delete_bookmark(
            user_id=user2.id,
            bookmark_id=bookmark['id']
        )


def test_search_bookmarks_empty_query(sample_data):
    """Test search with empty query."""
    result = BookmarkService.search_bookmarks(
        user_id=sample_data['user'].id,
        search_query=''
    )
    
    assert result == []


def test_search_bookmarks_with_results(sample_data):
    """Test search with matching results."""
    # Create bookmarks
    BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='Python programming language'
    )
    
    BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=1,
        note='JavaScript is also programming'
    )
    
    # Search for "programming"
    result = BookmarkService.search_bookmarks(
        user_id=sample_data['user'].id,
        search_query='programming',
        limit=10
    )
    
    assert len(result) == 2
    for bookmark in result:
        assert 'programming' in bookmark['note'].lower()


def test_export_bookmarks_empty(sample_data):
    """Test exporting bookmarks when user has none."""
    result = BookmarkService.export_bookmarks(sample_data['user'].id)
    
    assert "No bookmarks found for export." in result


def test_export_bookmarks_with_data(sample_data):
    """Test exporting bookmarks with data."""
    # Create bookmark
    BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0,
        note='Test export note'
    )
    
    result = BookmarkService.export_bookmarks(sample_data['user'].id)
    
    assert "Subtitle Learning Bookmarks Export" in result
    assert "Test Movie 1" in result  # Movie title
    assert "Test export note" in result
    assert "Alignment #1" in result


def test_export_bookmarks_invalid_format(sample_data):
    """Test exporting with invalid format."""
    with pytest.raises(BookmarkServiceError, match="Only 'text' format is currently supported"):
        BookmarkService.export_bookmarks(
            user_id=sample_data['user'].id,
            format='json'
        )


def test_enrich_bookmark_data(sample_data):
    """Test bookmark data enrichment with content preview."""
    # Create bookmark
    bookmark_data = BookmarkService.create_bookmark(
        user_id=sample_data['user'].id,
        sub_link_id=sample_data['sub_link'].id,
        alignment_index=0
    )
    
    # Check enriched data
    assert 'movie_title' in bookmark_data
    assert bookmark_data['movie_title'] == 'Test Movie 1'
    assert 'from_language' in bookmark_data
    assert bookmark_data['from_language'] == 'English'
    assert 'to_language' in bookmark_data
    assert bookmark_data['to_language'] == 'Spanish'
    assert 'content_preview' in bookmark_data