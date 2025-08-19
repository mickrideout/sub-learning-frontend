"""Subtitle API endpoints for subtitle retrieval and availability checking."""
from flask import jsonify, request
from flask_login import login_required, current_user
from app.blueprints.api import api_bp
from app.services.subtitle_service import SubtitleService
import logging

logger = logging.getLogger(__name__)


@api_bp.route('/movies/<int:movie_id>/subtitles', methods=['GET'])
@login_required
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