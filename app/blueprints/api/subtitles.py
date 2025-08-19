"""Subtitle API endpoints for subtitle retrieval and availability checking."""
from flask import jsonify, request, g
from flask_login import login_required, current_user
from app.blueprints.api import api_bp
from app.services.subtitle_service import SubtitleService
from app.models.subtitle import SubLink, SubLinkLine, SubLine, UserProgress
from app import db
import logging
import time
from functools import wraps

# Simple rate limiting storage (in production, use Redis)
_rate_limit_storage = {}

def rate_limit(requests_per_minute: int = 60):
    """Simple rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(current_user, 'id', 'anonymous')
            now = time.time()
            window_start = now - 60  # 1 minute window
            
            if user_id not in _rate_limit_storage:
                _rate_limit_storage[user_id] = []
            
            # Clean old requests
            _rate_limit_storage[user_id] = [
                req_time for req_time in _rate_limit_storage[user_id] 
                if req_time > window_start
            ]
            
            if len(_rate_limit_storage[user_id]) >= requests_per_minute:
                return jsonify({
                    'error': 'Rate limit exceeded. Too many requests.',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }), 429
            
            _rate_limit_storage[user_id].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

logger = logging.getLogger(__name__)


def verify_sub_link_access(user_id, sub_link_id):
    """Verify user has access to the specific language pair."""
    sub_link = SubLink.query.get(sub_link_id)
    if not sub_link:
        return False
    
    # Access control based on user's language preferences
    user = current_user
    if not user.native_language_id or not user.target_language_id:
        return False
    
    # Check if the sub_link matches user's language preferences
    valid_language_pair = (
        (sub_link.fromlang == user.native_language_id and sub_link.tolang == user.target_language_id) or
        (sub_link.fromlang == user.target_language_id and sub_link.tolang == user.native_language_id)
    )
    
    return valid_language_pair


@api_bp.route('/movies/<int:movie_id>/subtitles', methods=['GET'])
@login_required
@rate_limit(30)  # 30 requests per minute
def get_movie_subtitles(movie_id):
    """
    Retrieve subtitle content for a specific movie and language.
    
    Path Parameters:
        movie_id (int): Movie ID for subtitle retrieval
        
    Query Parameters:
        lang (int): Language ID for subtitle content
    
    Returns:
        JSON response with subtitle lines array containing sequence and content
    """
    try:
        # Validate movie_id parameter
        if movie_id <= 0:
            return jsonify({
                'error': 'Invalid movie ID. Must be a positive integer.',
                'code': 'INVALID_MOVIE_ID'
            }), 400

        # Get language parameter
        language_id = request.args.get('lang')
        if not language_id:
            return jsonify({
                'error': 'Language parameter (lang) is required.',
                'code': 'MISSING_LANGUAGE_PARAMETER'
            }), 400

        try:
            language_id = int(language_id)
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Invalid language ID. Must be a positive integer.',
                'code': 'INVALID_LANGUAGE_ID'
            }), 400

        if language_id <= 0:
            return jsonify({
                'error': 'Invalid language ID. Must be a positive integer.',
                'code': 'INVALID_LANGUAGE_ID'
            }), 400

        # Check if user has language preferences set
        if not current_user.native_language_id or not current_user.target_language_id:
            return jsonify({
                'error': 'Language preferences not set. Please update your profile.',
                'code': 'MISSING_LANGUAGE_PREFERENCES'
            }), 400

        # Validate user access to subtitle content
        if not SubtitleService.validate_subtitle_access(
            movie_id, language_id, 
            current_user.native_language_id, 
            current_user.target_language_id
        ):
            return jsonify({
                'error': 'Access denied. You can only access subtitles for your configured language pair.',
                'code': 'ACCESS_DENIED'
            }), 403

        # Get subtitle content
        subtitle_lines = SubtitleService.get_subtitle_content(movie_id, language_id)
        
        if not subtitle_lines:
            return jsonify({
                'error': 'No subtitle content found for the specified movie and language.',
                'code': 'SUBTITLES_NOT_FOUND'
            }), 404

        # Validate subtitle data integrity
        if not SubtitleService.validate_subtitle_data(subtitle_lines):
            logger.error(f"Invalid subtitle data integrity for movie {movie_id}, language {language_id}")
            return jsonify({
                'error': 'Subtitle data integrity error. Please try again later.',
                'code': 'DATA_INTEGRITY_ERROR'
            }), 500

        response_data = {
            'movie_id': movie_id,
            'language_id': language_id,
            'subtitle_lines': subtitle_lines,
            'total_lines': len(subtitle_lines),
            'user_language_pair': {
                'native_language_id': current_user.native_language_id,
                'target_language_id': current_user.target_language_id
            }
        }

        # Add caching headers for performance optimization
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'private, max-age=3600'  # 1 hour cache
        response.headers['ETag'] = f'"{movie_id}-{language_id}-{len(subtitle_lines)}"'
        
        logger.info(f"Retrieved {len(subtitle_lines)} subtitle lines for movie {movie_id}, language {language_id}")
        return response, 200

    except ValueError as e:
        logger.warning(f"Validation error for subtitle retrieval: {str(e)}")
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error retrieving subtitles for movie {movie_id}: {str(e)}")
        return jsonify({
            'error': 'Internal server error. Please try again later.',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/movies/<int:movie_id>/subtitles/availability', methods=['GET'])
@login_required
@rate_limit(60)  # 60 requests per minute for availability checks
def get_subtitle_availability(movie_id):
    """
    Check subtitle availability for a specific movie.
    
    Path Parameters:
        movie_id (int): Movie ID to check subtitle availability for
    
    Returns:
        JSON response with available language options for the movie
    """
    try:
        # Validate movie_id parameter
        if movie_id <= 0:
            return jsonify({
                'error': 'Invalid movie ID. Must be a positive integer.',
                'code': 'INVALID_MOVIE_ID'
            }), 400

        # Check if user has language preferences set
        if not current_user.native_language_id or not current_user.target_language_id:
            return jsonify({
                'error': 'Language preferences not set. Please update your profile.',
                'code': 'MISSING_LANGUAGE_PREFERENCES'
            }), 400

        # Get available languages for the movie
        available_languages = SubtitleService.get_available_languages(movie_id)
        
        # Filter languages based on user's language pair
        user_languages = {current_user.native_language_id, current_user.target_language_id}
        accessible_languages = [
            lang for lang in available_languages 
            if lang['id'] in user_languages
        ]

        response_data = {
            'movie_id': movie_id,
            'available_languages': accessible_languages,
            'total_available': len(accessible_languages),
            'user_language_pair': {
                'native_language_id': current_user.native_language_id,
                'target_language_id': current_user.target_language_id
            },
            'has_subtitles': len(accessible_languages) > 0
        }

        # Add caching headers
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'private, max-age=1800'  # 30 minutes cache
        
        logger.info(f"Retrieved subtitle availability for movie {movie_id}: {len(accessible_languages)} accessible languages")
        return response, 200

    except ValueError as e:
        logger.warning(f"Validation error for subtitle availability check: {str(e)}")
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error checking subtitle availability for movie {movie_id}: {str(e)}")
        return jsonify({
            'error': 'Internal server error. Please try again later.',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/subtitles/cache/stats', methods=['GET'])
@login_required
def get_cache_stats():
    """
    Get subtitle cache performance statistics.
    
    Returns:
        JSON response with cache performance metrics
    """
    try:
        # Only allow admin users to view cache stats (basic security)
        # For now, allow all authenticated users - can be restricted later
        cache_stats = SubtitleService.get_cache_stats()
        
        return jsonify({
            'cache_statistics': cache_stats,
            'timestamp': cache_stats.get('timestamp', None)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving cache statistics: {str(e)}")
        return jsonify({
            'error': 'Internal server error. Please try again later.',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/subtitles/<int:sub_link_id>', methods=['GET'])
@login_required
@rate_limit(10)  # 10 requests per minute for alignment data
def get_subtitle_alignments(sub_link_id):
    """
    Retrieve paginated alignment data for subtitle learning interface.
    
    Path Parameters:
        sub_link_id (int): SubLink ID for alignment retrieval
        
    Query Parameters:
        start_index (int): Starting alignment index (default: 0)
        limit (int): Maximum alignments to return (default: 50, max: 50)
    
    Returns:
        JSON response with alignment data and pagination metadata
    """
    try:
        # Validate sub_link_id parameter
        if sub_link_id <= 0:
            return jsonify({
                'error': 'Invalid sub_link_id. Must be a positive integer.',
                'code': 'INVALID_SUB_LINK_ID'
            }), 400

        # Verify user access to this language pair
        if not verify_sub_link_access(current_user.id, sub_link_id):
            return jsonify({
                'error': 'Access denied. Invalid language pair for user.',
                'code': 'ACCESS_DENIED'
            }), 403

        # Get pagination parameters
        try:
            start_index = int(request.args.get('start_index', 0))
            limit = min(int(request.args.get('limit', 50)), 50)  # Max 50 alignments
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Invalid pagination parameters. start_index and limit must be integers.',
                'code': 'INVALID_PAGINATION_PARAMETERS'
            }), 400

        if start_index < 0 or limit <= 0:
            return jsonify({
                'error': 'Invalid pagination parameters. start_index >= 0 and limit > 0 required.',
                'code': 'INVALID_PAGINATION_PARAMETERS'
            }), 400

        # Get alignment data
        sub_link_line = SubLinkLine.query.filter_by(sub_link_id=sub_link_id).first()
        if not sub_link_line:
            return jsonify({
                'error': 'No alignment data found for this language pair.',
                'code': 'ALIGNMENTS_NOT_FOUND'
            }), 404

        link_data = sub_link_line.link_data
        if not link_data or not isinstance(link_data, list):
            return jsonify({
                'error': 'Invalid alignment data format.',
                'code': 'INVALID_ALIGNMENT_DATA'
            }), 500

        total_alignments = len(link_data)
        
        # Apply pagination
        end_index = min(start_index + limit, total_alignments)
        paginated_alignments = link_data[start_index:end_index]

        # Get source and target subtitle lines for the paginated alignments
        source_line_ids = set()
        target_line_ids = set()
        
        for alignment in paginated_alignments:
            if isinstance(alignment, list) and len(alignment) >= 2:
                if isinstance(alignment[0], list):
                    source_line_ids.update(alignment[0])
                if isinstance(alignment[1], list):
                    target_line_ids.update(alignment[1])

        # Fetch subtitle content
        all_line_ids = source_line_ids.union(target_line_ids)
        subtitle_lines = {}
        if all_line_ids:
            lines = SubLine.query.filter(SubLine.id.in_(all_line_ids)).all()
            subtitle_lines = {line.id: line.to_dict() for line in lines}

        # Format alignment data for response
        formatted_alignments = []
        for i, alignment in enumerate(paginated_alignments):
            if isinstance(alignment, list) and len(alignment) >= 2:
                formatted_alignment = {
                    'index': start_index + i,
                    'source_lines': alignment[0] if isinstance(alignment[0], list) else [],
                    'target_lines': alignment[1] if isinstance(alignment[1], list) else []
                }
                formatted_alignments.append(formatted_alignment)

        response_data = {
            'sub_link_id': sub_link_id,
            'alignments': formatted_alignments,
            'subtitle_lines': subtitle_lines,
            'pagination': {
                'start_index': start_index,
                'limit': limit,
                'total_alignments': total_alignments,
                'current_index': start_index,
                'has_more': end_index < total_alignments
            }
        }

        # Add caching headers
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'private, max-age=1800'  # 30 minutes cache
        
        logger.info(f"Retrieved {len(formatted_alignments)} alignments for sub_link {sub_link_id}")
        return response, 200

    except ValueError as e:
        logger.warning(f"Validation error for alignment retrieval: {str(e)}")
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error retrieving alignments for sub_link {sub_link_id}: {str(e)}")
        return jsonify({
            'error': 'Internal server error. Please try again later.',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/progress/<int:sub_link_id>', methods=['GET'])
@login_required
def get_user_progress(sub_link_id):
    """
    Retrieve current user progress for a subtitle learning session.
    
    Path Parameters:
        sub_link_id (int): SubLink ID for progress retrieval
    
    Returns:
        JSON response with current progress data
    """
    try:
        # Validate sub_link_id parameter
        if sub_link_id <= 0:
            return jsonify({
                'error': 'Invalid sub_link_id. Must be a positive integer.',
                'code': 'INVALID_SUB_LINK_ID'
            }), 400

        # Verify user access to this language pair
        if not verify_sub_link_access(current_user.id, sub_link_id):
            return jsonify({
                'error': 'Access denied. Invalid language pair for user.',
                'code': 'ACCESS_DENIED'
            }), 403

        # Get user progress
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            sub_link_id=sub_link_id
        ).first()

        if not progress:
            # Create new progress entry if none exists
            progress = UserProgress(
                user_id=current_user.id,
                sub_link_id=sub_link_id,
                current_alignment_index=0
            )
            db.session.add(progress)
            db.session.commit()

        response_data = progress.to_dict()
        
        logger.info(f"Retrieved progress for user {current_user.id}, sub_link {sub_link_id}")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error retrieving progress for sub_link {sub_link_id}: {str(e)}")
        return jsonify({
            'error': 'Internal server error. Please try again later.',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/progress/<int:sub_link_id>', methods=['PUT'])
@login_required
def update_user_progress(sub_link_id):
    """
    Update user progress for a subtitle learning session.
    
    Path Parameters:
        sub_link_id (int): SubLink ID for progress update
        
    Request Body:
        {
            "current_alignment_index": int  // New alignment index
        }
    
    Returns:
        JSON response with updated progress data
    """
    try:
        # Validate sub_link_id parameter
        if sub_link_id <= 0:
            return jsonify({
                'error': 'Invalid sub_link_id. Must be a positive integer.',
                'code': 'INVALID_SUB_LINK_ID'
            }), 400

        # Verify user access to this language pair
        if not verify_sub_link_access(current_user.id, sub_link_id):
            return jsonify({
                'error': 'Access denied. Invalid language pair for user.',
                'code': 'ACCESS_DENIED'
            }), 403

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body must contain JSON data.',
                'code': 'MISSING_REQUEST_DATA'
            }), 400

        # Validate alignment index
        try:
            new_index = int(data.get('current_alignment_index', 0))
        except (ValueError, TypeError):
            return jsonify({
                'error': 'current_alignment_index must be a valid integer.',
                'code': 'INVALID_ALIGNMENT_INDEX'
            }), 400

        if new_index < 0:
            return jsonify({
                'error': 'current_alignment_index must be >= 0.',
                'code': 'INVALID_ALIGNMENT_INDEX'
            }), 400

        # Update progress with database transaction
        with db.session.begin():
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                sub_link_id=sub_link_id
            ).first()

            if not progress:
                # Create new progress entry
                progress = UserProgress(
                    user_id=current_user.id,
                    sub_link_id=sub_link_id,
                    current_alignment_index=new_index
                )
                db.session.add(progress)
            else:
                # Update existing progress
                progress.current_alignment_index = new_index
                progress.last_accessed = db.func.current_timestamp()

            db.session.commit()

        response_data = progress.to_dict()
        
        logger.info(f"Updated progress for user {current_user.id}, sub_link {sub_link_id} to index {new_index}")
        return jsonify(response_data), 200

    except ValueError as e:
        logger.warning(f"Validation error for progress update: {str(e)}")
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        logger.error(f"Error updating progress for sub_link {sub_link_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error. Please try again later.',
            'code': 'INTERNAL_ERROR'
        }), 500