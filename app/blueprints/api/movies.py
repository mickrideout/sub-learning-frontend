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
    Get available movies filtered by user's language pair and optional search query.
    
    Returns movies that have subtitles available for the user's
    native_language_id and target_language_id combination, optionally
    filtered by a search query for partial title matching.
    
    Query Parameters:
        search (str, optional): Search query for partial title matching (case-insensitive)
    
    Returns:
        JSON response with filtered movies list and search metadata
    """
    try:
        # Check if user has language preferences set
        if not current_user.native_language_id or not current_user.target_language_id:
            return jsonify({
                'error': 'Language preferences not set. Please update your profile.',
                'code': 'MISSING_LANGUAGE_PREFERENCES'
            }), 400

        # Get optional search query parameter
        search_query = request.args.get('search', '').strip()

        # Use content service to get available movies with optional search
        movies = ContentService.get_available_movies(
            current_user.native_language_id,
            current_user.target_language_id,
            search_query=search_query if search_query else None
        )

        response_data = {
            'movies': movies,
            'language_pair': {
                'native_language_id': current_user.native_language_id,
                'target_language_id': current_user.target_language_id
            },
            'total_count': len(movies)
        }

        # Add search metadata if search query was provided
        if search_query:
            response_data['search'] = {
                'query': search_query,
                'result_count': len(movies)
            }

        return jsonify(response_data), 200

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