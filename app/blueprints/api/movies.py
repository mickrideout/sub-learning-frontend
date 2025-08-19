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
    Get available movies filtered by user's language pair and optional search query and letter filter.
    
    Returns movies that have subtitles available for the user's
    native_language_id and target_language_id combination, optionally
    filtered by a search query for partial title matching and/or alphabetical letter.
    
    Query Parameters:
        search (str, optional): Search query for partial title matching (case-insensitive)
        letter (str, optional): Letter filter (A-Z, #, or 'all')
    
    Returns:
        JSON response with filtered movies list and search/letter metadata
    """
    try:
        # Check if user has language preferences set
        if not current_user.native_language_id or not current_user.target_language_id:
            return jsonify({
                'error': 'Language preferences not set. Please update your profile.',
                'code': 'MISSING_LANGUAGE_PREFERENCES'
            }), 400

        # Get optional query parameters
        search_query = request.args.get('search', '').strip()
        letter_filter = request.args.get('letter', '').strip()

        # Use content service to get available movies with optional filters
        movies = ContentService.get_available_movies(
            current_user.native_language_id,
            current_user.target_language_id,
            search_query=search_query if search_query else None,
            letter_filter=letter_filter if letter_filter else None
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

        # Add letter filter metadata if letter filter was provided and not 'all'
        if letter_filter and letter_filter != 'all':
            response_data['letter_filter'] = {
                'letter': letter_filter,
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


@api_bp.route('/movies/letters', methods=['GET'])
@login_required
def get_letter_counts():
    """
    Get count of available movies for each letter (A-Z, #) for user's language pair.
    
    Returns counts of movies that have subtitles available for the user's
    native_language_id and target_language_id combination, grouped by first letter.
    Optionally filtered by search query.
    
    Query Parameters:
        search (str, optional): Search query to filter counts (case-insensitive)
    
    Returns:
        JSON response with letter counts and metadata
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

        # Use content service to get letter counts with optional search filter
        letter_counts = ContentService.get_letter_counts(
            current_user.native_language_id,
            current_user.target_language_id,
            search_query=search_query if search_query else None
        )

        # Create full alphabet with zero counts for missing letters
        full_alphabet = {}
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#':
            full_alphabet[letter] = letter_counts.get(letter, 0)

        response_data = {
            'letter_counts': full_alphabet,
            'language_pair': {
                'native_language_id': current_user.native_language_id,
                'target_language_id': current_user.target_language_id
            },
            'total_letters_with_movies': len([count for count in letter_counts.values() if count > 0])
        }

        # Add search metadata if search query was provided
        if search_query:
            response_data['search'] = {
                'query': search_query,
                'total_filtered_movies': sum(letter_counts.values())
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