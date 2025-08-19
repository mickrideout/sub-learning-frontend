"""Bookmark service for managing user subtitle bookmarks."""
from sqlalchemy import exc, and_, or_, text
from sqlalchemy.orm import exc as orm_exc
from app import db
from app.models.bookmark import Bookmark
from app.models.subtitle import SubLink, SubLinkLine, SubLine, SubTitle


class BookmarkServiceError(Exception):
    """Custom exception for bookmark service errors."""
    pass


class BookmarkService:
    """Service class for managing user bookmark operations."""
    
    @staticmethod
    def create_bookmark(user_id, sub_link_id, alignment_index, note=None):
        """
        Create a new bookmark for a specific subtitle alignment.
        
        Args:
            user_id (int): ID of the user creating the bookmark
            sub_link_id (int): ID of the subtitle link
            alignment_index (int): Index of the specific alignment in link_data array
            note (str, optional): User note about the bookmark
            
        Returns:
            dict: Created bookmark data with content preview
            
        Raises:
            BookmarkServiceError: If validation fails or database error occurs
        """
        try:
            # Validate inputs
            if alignment_index < 0:
                raise BookmarkServiceError("Alignment index cannot be negative")
            
            # Validate sub_link exists and get alignment data
            sub_link = db.session.get(SubLink, sub_link_id)
            if not sub_link:
                raise BookmarkServiceError(f"Subtitle link {sub_link_id} not found")
                
            alignment_data = SubLinkLine.query.filter_by(sub_link_id=sub_link_id).first()
            if not alignment_data or not alignment_data.link_data:
                raise BookmarkServiceError("No alignment data found for this subtitle link")
                
            total_alignments = len(alignment_data.link_data)
            if alignment_index >= total_alignments:
                raise BookmarkServiceError(f"Alignment index {alignment_index} exceeds available alignments ({total_alignments})")
            
            # Check for duplicate bookmark (unique constraint will also prevent this)
            existing_bookmark = Bookmark.query.filter_by(
                user_id=user_id,
                sub_link_id=sub_link_id,
                alignment_index=alignment_index,
                is_active=True
            ).first()
            
            if existing_bookmark:
                raise BookmarkServiceError("Bookmark already exists for this alignment")
            
            # Validate note length (optional constraint)
            if note and len(note) > 1000:
                raise BookmarkServiceError("Bookmark note cannot exceed 1000 characters")
            
            # Create new bookmark
            bookmark = Bookmark(
                user_id=user_id,
                sub_link_id=sub_link_id,
                alignment_index=alignment_index,
                note=note.strip() if note else None
            )
            db.session.add(bookmark)
            db.session.commit()
            
            return BookmarkService._enrich_bookmark_data(bookmark)
                
        except exc.IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise BookmarkServiceError("Bookmark already exists for this alignment")
            raise BookmarkServiceError(f"Database constraint violation: {str(e)}")
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise BookmarkServiceError(f"Database error creating bookmark: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise BookmarkServiceError(f"Error creating bookmark: {str(e)}")
    
    @staticmethod
    def get_user_bookmarks(user_id, search_query=None, limit=50, offset=0):
        """
        Get user bookmarks with content preview and movie details.
        
        Args:
            user_id (int): ID of the user
            search_query (str, optional): Search within bookmark content
            limit (int): Maximum number of bookmarks to return (max 100)
            offset (int): Number of bookmarks to skip for pagination
            
        Returns:
            dict: Paginated bookmark data with content previews and totals
            
        Raises:
            BookmarkServiceError: If database error occurs
        """
        try:
            # Enforce Pi performance limits
            limit = min(100, max(1, limit))
            offset = max(0, offset)
            
            # Build base query
            query = Bookmark.query.filter_by(user_id=user_id, is_active=True)
            
            # Add search functionality if provided
            if search_query and search_query.strip():
                # Join with SubLink and SubLinkLine to search content
                query = query.join(SubLink).join(SubLinkLine, SubLink.id == SubLinkLine.sub_link_id)
                # Use SQLite FTS if available, otherwise use LIKE search
                search_term = f"%{search_query.strip().lower()}%"
                query = query.filter(
                    or_(
                        Bookmark.note.ilike(search_term),
                        # Note: Content search would require JSON extraction which is complex
                        # For now, focus on note search
                    )
                )
            
            # Get total count for pagination
            total_count = query.count()
            
            # Get paginated results
            bookmarks = query.order_by(Bookmark.created_at.desc()).offset(offset).limit(limit).all()
            
            # Enrich with content data
            enriched_bookmarks = []
            for bookmark in bookmarks:
                enriched_bookmarks.append(BookmarkService._enrich_bookmark_data(bookmark))
            
            return {
                'bookmarks': enriched_bookmarks,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count
            }
            
        except exc.SQLAlchemyError as e:
            raise BookmarkServiceError(f"Database error retrieving bookmarks: {str(e)}")
        except Exception as e:
            raise BookmarkServiceError(f"Error retrieving bookmarks: {str(e)}")
    
    @staticmethod
    def delete_bookmark(user_id, bookmark_id):
        """
        Delete a bookmark (soft delete using is_active flag).
        
        Args:
            user_id (int): ID of the user
            bookmark_id (int): ID of the bookmark to delete
            
        Returns:
            dict: Confirmation with updated bookmark count
            
        Raises:
            BookmarkServiceError: If bookmark not found or database error occurs
        """
        try:
            # Find bookmark and validate ownership
            bookmark = Bookmark.query.filter_by(
                id=bookmark_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if not bookmark:
                raise BookmarkServiceError("Bookmark not found or already deleted")
            
            # Soft delete
            bookmark.is_active = False
            db.session.commit()
            
            # Get updated bookmark count
            remaining_count = Bookmark.query.filter_by(user_id=user_id, is_active=True).count()
            
            return {
                'message': 'Bookmark deleted successfully',
                'bookmark_id': bookmark_id,
                'remaining_bookmarks': remaining_count
            }
                
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise BookmarkServiceError(f"Database error deleting bookmark: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise BookmarkServiceError(f"Error deleting bookmark: {str(e)}")
    
    @staticmethod
    def search_bookmarks(user_id, search_query, limit=50):
        """
        Search within user's bookmarked content for specific phrases or words.
        
        Args:
            user_id (int): ID of the user
            search_query (str): Search term for content filtering
            limit (int): Maximum number of results to return
            
        Returns:
            list: Matching bookmarks with highlighted search terms
            
        Raises:
            BookmarkServiceError: If database error occurs
        """
        try:
            if not search_query or not search_query.strip():
                return []
            
            search_term = search_query.strip().lower()
            limit = min(100, max(1, limit))
            
            # Search in bookmark notes
            bookmarks = Bookmark.query.filter(
                and_(
                    Bookmark.user_id == user_id,
                    Bookmark.is_active == True,
                    Bookmark.note.ilike(f"%{search_term}%")
                )
            ).order_by(Bookmark.created_at.desc()).limit(limit).all()
            
            # Enrich with content data and search highlighting
            results = []
            for bookmark in bookmarks:
                enriched = BookmarkService._enrich_bookmark_data(bookmark)
                # Add search highlight info
                if bookmark.note and search_term in bookmark.note.lower():
                    enriched['search_highlight'] = 'note'
                results.append(enriched)
            
            return results
            
        except exc.SQLAlchemyError as e:
            raise BookmarkServiceError(f"Database error searching bookmarks: {str(e)}")
        except Exception as e:
            raise BookmarkServiceError(f"Error searching bookmarks: {str(e)}")
    
    @staticmethod
    def export_bookmarks(user_id, format='text'):
        """
        Export user bookmarks to text format for external study tools.
        
        Args:
            user_id (int): ID of the user
            format (str): Export format ('text' is currently supported)
            
        Returns:
            str: Formatted bookmark export data
            
        Raises:
            BookmarkServiceError: If database error occurs
        """
        try:
            if format != 'text':
                raise BookmarkServiceError("Only 'text' format is currently supported")
            
            bookmarks = Bookmark.query.filter_by(
                user_id=user_id,
                is_active=True
            ).order_by(Bookmark.created_at.desc()).all()
            
            if not bookmarks:
                return "No bookmarks found for export."
            
            export_lines = ["Subtitle Learning Bookmarks Export", "="*40, ""]
            
            for bookmark in bookmarks:
                enriched = BookmarkService._enrich_bookmark_data(bookmark)
                
                export_lines.append(f"Movie: {enriched.get('movie_title', 'Unknown')}")
                export_lines.append(f"Languages: {enriched.get('from_language', 'Unknown')} → {enriched.get('to_language', 'Unknown')}")
                export_lines.append(f"Alignment #{bookmark.alignment_index + 1}")
                
                if enriched.get('content_preview'):
                    export_lines.append(f"Content: {enriched['content_preview']}")
                
                if bookmark.note:
                    export_lines.append(f"Note: {bookmark.note}")
                
                export_lines.append(f"Bookmarked: {bookmark.created_at.strftime('%Y-%m-%d %H:%M')}")
                export_lines.append("-" * 30)
                export_lines.append("")
            
            return "\n".join(export_lines)
            
        except exc.SQLAlchemyError as e:
            raise BookmarkServiceError(f"Database error exporting bookmarks: {str(e)}")
        except Exception as e:
            raise BookmarkServiceError(f"Error exporting bookmarks: {str(e)}")
    
    @staticmethod
    def _enrich_bookmark_data(bookmark):
        """
        Enrich bookmark data with content preview and movie details.
        
        Args:
            bookmark (Bookmark): Bookmark instance
            
        Returns:
            dict: Enriched bookmark data with content preview
        """
        try:
            bookmark_dict = bookmark.to_dict()
            
            # Get SubLink and related data
            sub_link = bookmark.sub_link
            alignment_data = SubLinkLine.query.filter_by(sub_link_id=bookmark.sub_link_id).first()
            
            if sub_link and alignment_data and alignment_data.link_data:
                # Get movie titles
                from_movie = sub_link.from_subtitle
                to_movie = sub_link.to_subtitle
                
                bookmark_dict['movie_title'] = from_movie.title if from_movie else 'Unknown'
                bookmark_dict['from_language'] = sub_link.from_language.display_name if sub_link.from_language else 'Unknown'
                bookmark_dict['to_language'] = sub_link.to_language.display_name if sub_link.to_language else 'Unknown'
                
                # Get content preview for this alignment
                if bookmark.alignment_index < len(alignment_data.link_data):
                    alignment_pair = alignment_data.link_data[bookmark.alignment_index]
                    
                    if len(alignment_pair) >= 2 and alignment_pair[0] and alignment_pair[1]:
                        # Get first line from each language as preview
                        source_line_ids = alignment_pair[0][:1]  # First source line
                        target_line_ids = alignment_pair[1][:1]  # First target line
                        
                        source_content = ""
                        target_content = ""
                        
                        if source_line_ids:
                            source_line = SubLine.query.get(source_line_ids[0])
                            if source_line:
                                source_content = source_line.content[:100]  # Truncate for preview
                        
                        if target_line_ids:
                            target_line = SubLine.query.get(target_line_ids[0])
                            if target_line:
                                target_content = target_line.content[:100]  # Truncate for preview
                        
                        bookmark_dict['content_preview'] = f"{source_content} | {target_content}"
                        bookmark_dict['source_content'] = source_content
                        bookmark_dict['target_content'] = target_content
                
            return bookmark_dict
            
        except Exception:
            # If enrichment fails, return basic bookmark data
            return bookmark.to_dict()