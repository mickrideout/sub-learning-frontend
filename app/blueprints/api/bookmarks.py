"""Bookmark API endpoints for user bookmark management."""
from flask import jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import exc
from app.blueprints.api import api_bp
from app.services.bookmark_service import BookmarkService, BookmarkServiceError
from app import db


@api_bp.route('/bookmarks', methods=['POST'])
@login_required
def create_bookmark():
    """
    Create a new bookmark for a specific subtitle alignment.
    
    Expected JSON payload:
    {
        "sub_link_id": integer,
        "alignment_index": integer,
        "note": string (optional)
    }
    
    Returns:
        JSON response with created bookmark data and content preview
    """
    try:
        # Handle JSON parsing errors
        try:
            data = request.get_json()
        except Exception:
            return jsonify({
                'error': 'Invalid JSON data in request body',
                'code': 'INVALID_JSON'
            }), 400

        if not data:
            return jsonify({
                'error': 'Request body must contain JSON data',
                'code': 'MISSING_DATA'
            }), 400

        # Extract required fields
        sub_link_id = data.get('sub_link_id')
        alignment_index = data.get('alignment_index')
        note = data.get('note')

        # Validate required fields
        if sub_link_id is None:
            return jsonify({
                'error': 'sub_link_id is required',
                'code': 'MISSING_SUB_LINK_ID'
            }), 400

        if alignment_index is None:
            return jsonify({
                'error': 'alignment_index is required',
                'code': 'MISSING_ALIGNMENT_INDEX'
            }), 400

        # Validate field types and values
        try:
            sub_link_id = int(sub_link_id)
            alignment_index = int(alignment_index)

            if sub_link_id <= 0:
                raise ValueError("sub_link_id must be positive")
            if alignment_index < 0:
                raise ValueError("alignment_index must be non-negative")

        except (ValueError, TypeError) as e:
            return jsonify({
                'error': f'Invalid field values: {str(e)}',
                'code': 'INVALID_FIELD_VALUES'
            }), 400

        # Validate note if provided
        if note is not None:
            if not isinstance(note, str):
                return jsonify({
                    'error': 'Note must be a string',
                    'code': 'INVALID_NOTE_TYPE'
                }), 400
            if len(note.strip()) == 0:
                note = None  # Convert empty string to None

        # Create bookmark using service layer
        bookmark_data = BookmarkService.create_bookmark(
            user_id=current_user.id,
            sub_link_id=sub_link_id,
            alignment_index=alignment_index,
            note=note
        )

        return jsonify({
            'message': 'Bookmark created successfully',
            'bookmark': bookmark_data
        }), 201
        
    except BookmarkServiceError as e:
        error_message = str(e)
        if "not found" in error_message:
            return jsonify({
                'error': error_message,
                'code': 'RESOURCE_NOT_FOUND'
            }), 404
        elif "already exists" in error_message:
            return jsonify({
                'error': error_message,
                'code': 'BOOKMARK_ALREADY_EXISTS'
            }), 409
        elif ("exceeds" in error_message or "cannot be negative" in error_message or 
              "cannot exceed" in error_message):
            return jsonify({
                'error': error_message,
                'code': 'INVALID_BOOKMARK_DATA'
            }), 400
        else:
            return jsonify({
                'error': error_message,
                'code': 'BOOKMARK_SERVICE_ERROR'
            }), 400
            
    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            'error': 'Database error occurred while creating bookmark',
            'code': 'DATABASE_ERROR'
        }), 500
    except Exception:
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/bookmarks', methods=['GET'])
@login_required
def get_bookmarks():
    """
    Get user bookmarks with content preview and movie details.
    
    Query parameters:
        search (str): Search term for filtering bookmark content
        limit (int): Maximum number of bookmarks to return (default 50, max 100)
        offset (int): Number of bookmarks to skip for pagination (default 0)
        
    Returns:
        JSON response with paginated bookmark list and content previews
    """
    try:
        # Get query parameters with validation
        search_query = request.args.get('search', '').strip()
        
        try:
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            
            # Enforce Pi performance limits
            if limit < 1:
                limit = 50
            elif limit > 100:
                limit = 100
            if offset < 0:
                offset = 0
                
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Limit and offset must be valid integers',
                'code': 'INVALID_PAGINATION_PARAMS'
            }), 400

        # Get bookmarks using service layer
        result = BookmarkService.get_user_bookmarks(
            user_id=current_user.id,
            search_query=search_query if search_query else None,
            limit=limit,
            offset=offset
        )

        return jsonify(result), 200
        
    except BookmarkServiceError as e:
        return jsonify({
            'error': str(e),
            'code': 'BOOKMARK_SERVICE_ERROR'
        }), 400
        
    except exc.SQLAlchemyError:
        return jsonify({
            'error': 'Database connection error. Please try again later.',
            'code': 'DATABASE_ERROR'
        }), 500
    except Exception:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/bookmarks/<int:bookmark_id>', methods=['DELETE'])
@login_required
def delete_bookmark(bookmark_id):
    """
    Delete a specific bookmark by ID with user ownership validation.
    
    Args:
        bookmark_id (int): ID of the bookmark to delete
        
    Returns:
        JSON response with deletion confirmation and updated bookmark count
    """
    try:
        # Validate bookmark_id
        if bookmark_id <= 0:
            return jsonify({
                'error': 'Invalid bookmark ID',
                'code': 'INVALID_BOOKMARK_ID'
            }), 400

        # Delete bookmark using service layer
        result = BookmarkService.delete_bookmark(
            user_id=current_user.id,
            bookmark_id=bookmark_id
        )

        return jsonify(result), 200
        
    except BookmarkServiceError as e:
        error_message = str(e)
        if "not found" in error_message or "already deleted" in error_message:
            return jsonify({
                'error': error_message,
                'code': 'BOOKMARK_NOT_FOUND'
            }), 404
        else:
            return jsonify({
                'error': error_message,
                'code': 'BOOKMARK_SERVICE_ERROR'
            }), 400
            
    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            'error': 'Database error occurred while deleting bookmark',
            'code': 'DATABASE_ERROR'
        }), 500
    except Exception:
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/bookmarks/search', methods=['GET'])
@login_required
def search_bookmarks():
    """
    Search within user's bookmarked content for specific phrases or words.
    
    Query parameters:
        q (str): Search query for content filtering (required)
        limit (int): Maximum number of results to return (default 50, max 100)
        
    Returns:
        JSON response with matching bookmarks and search highlights
    """
    try:
        # Get search query
        search_query = request.args.get('q', '').strip()
        
        if not search_query:
            return jsonify({
                'error': 'Search query (q) parameter is required',
                'code': 'MISSING_SEARCH_QUERY'
            }), 400

        # Get limit parameter with validation
        try:
            limit = int(request.args.get('limit', 50))
            # Enforce reasonable limits for Pi performance
            if limit < 1:
                limit = 50
            elif limit > 100:
                limit = 100
        except (ValueError, TypeError):
            limit = 50

        # Search bookmarks using service layer
        results = BookmarkService.search_bookmarks(
            user_id=current_user.id,
            search_query=search_query,
            limit=limit
        )

        return jsonify({
            'search_query': search_query,
            'results': results,
            'count': len(results)
        }), 200
        
    except BookmarkServiceError as e:
        return jsonify({
            'error': str(e),
            'code': 'BOOKMARK_SERVICE_ERROR'
        }), 400
        
    except exc.SQLAlchemyError:
        return jsonify({
            'error': 'Database connection error. Please try again later.',
            'code': 'DATABASE_ERROR'
        }), 500
    except Exception:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/bookmarks/export', methods=['GET'])
@login_required
def export_bookmarks():
    """
    Export user bookmarks to text format for external study tools.
    
    Query parameters:
        format (str): Export format, currently only 'text' is supported (default 'text')
        
    Returns:
        JSON response with exported bookmark data as text string
    """
    try:
        # Get format parameter
        export_format = request.args.get('format', 'text').lower()
        
        if export_format != 'text':
            return jsonify({
                'error': 'Only "text" format is currently supported',
                'code': 'UNSUPPORTED_FORMAT'
            }), 400

        # Export bookmarks using service layer
        export_data = BookmarkService.export_bookmarks(
            user_id=current_user.id,
            format=export_format
        )

        return jsonify({
            'format': export_format,
            'export_data': export_data,
            'generated_at': db.func.current_timestamp()
        }), 200
        
    except BookmarkServiceError as e:
        return jsonify({
            'error': str(e),
            'code': 'BOOKMARK_SERVICE_ERROR'
        }), 400
        
    except exc.SQLAlchemyError:
        return jsonify({
            'error': 'Database connection error. Please try again later.',
            'code': 'DATABASE_ERROR'
        }), 500
    except Exception:
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500