"""API routes and endpoints."""
from flask import jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import exc
from app.blueprints.api import api_bp
from app.models.language import Language
from app import db


@api_bp.route('/languages', methods=['GET'])
def get_languages():
    """
    Get all available languages for language selection.

    Returns:
        JSON response with all languages sorted alphabetically by display_name
    """
    try:
        languages = Language.query.order_by(Language.display_name).all()

        return jsonify({
            'languages': [language.to_dict() for language in languages]
        }), 200

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


@api_bp.route('/user/languages', methods=['POST'])
@login_required
def update_user_languages():
    """
    Update user's native and target language preferences.

    Expected JSON payload:
    {
        "native_language_id": integer,
        "target_language_id": integer
    }

    Returns:
        JSON response with updated user language preferences
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body must contain JSON data',
                'code': 'MISSING_DATA'
            }), 400

        native_language_id = data.get('native_language_id')
        target_language_id = data.get('target_language_id')

        # Validate required fields
        if not native_language_id or not target_language_id:
            return jsonify({
                'error': 'Both native_language_id and target_language_id are required',
                'code': 'MISSING_FIELDS'
            }), 400

        # Validate that languages are different
        if native_language_id == target_language_id:
            return jsonify({
                'error': 'Native language and target language must be different',
                'code': 'SAME_LANGUAGE_ERROR'
            }), 400

        # Validate that language IDs are positive integers
        try:
            native_language_id = int(native_language_id)
            target_language_id = int(target_language_id)

            if native_language_id <= 0 or target_language_id <= 0:
                raise ValueError("Language IDs must be positive integers")

        except (ValueError, TypeError):
            return jsonify({
                'error': 'Language IDs must be positive integers',
                'code': 'INVALID_LANGUAGE_ID'
            }), 400

        # Verify that both languages exist in the database
        native_language = Language.query.get(native_language_id)
        target_language = Language.query.get(target_language_id)

        if not native_language:
            return jsonify({
                'error': 'Native language not found',
                'code': 'INVALID_NATIVE_LANGUAGE'
            }), 404

        if not target_language:
            return jsonify({
                'error': 'Target language not found',
                'code': 'INVALID_TARGET_LANGUAGE'
            }), 404

        # Update user's language preferences
        current_user.native_language_id = native_language_id
        current_user.target_language_id = target_language_id

        db.session.commit()

        return jsonify({
            'message': 'Language preferences updated successfully',
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'native_language': native_language.to_dict(),
                'target_language': target_language.to_dict()
            }
        }), 200

    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            'error': 'Database error occurred while updating languages',
            'code': 'DATABASE_ERROR'
        }), 500
    except Exception:
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500
