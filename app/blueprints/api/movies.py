"""Movie API endpoints for catalog display and filtering."""
from flask import jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import exc
from app.blueprints.api import api_bp
from app.services.content_service import ContentService


@api_bp.route('/movies', methods=['GET'])
@login_required
def get_movies():
    """
    Get available movies filtered by user's language pair.
    
    Returns movies that have subtitles available for the user's
    native_language_id and target_language_id combination.
    
    Returns:
        JSON response with filtered movies list
    """
    try:
        # Check if user has language preferences set
        if not current_user.native_language_id or not current_user.target_language_id:
            return jsonify({
                'error': 'Language preferences not set. Please update your profile.',
                'code': 'MISSING_LANGUAGE_PREFERENCES'
            }), 400

        # Use content service to get available movies
        movies = ContentService.get_available_movies(
            current_user.native_language_id,
            current_user.target_language_id
        )

        return jsonify({
            'movies': movies,
            'language_pair': {
                'native_language_id': current_user.native_language_id,
                'target_language_id': current_user.target_language_id
            },
            'total_count': len(movies)
        }), 200

    except ValueError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Database connection error. Please try again later.',
            'code': 'DATABASE_ERROR'
        }), 500