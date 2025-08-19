"""Progress API endpoints for user learning progress tracking."""
from flask import jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import exc
from app.blueprints.api import api_bp
from app.services.progress_service import ProgressService, ProgressServiceError
from app import db


@api_bp.route('/progress/<int:sub_link_id>', methods=['GET'])
@login_required
def get_progress(sub_link_id):
    """
    Get user progress for a specific subtitle link.
    
    Args:
        sub_link_id (int): ID of the subtitle link
        
    Returns:
        JSON response with progress data and completion statistics
        404 if no progress exists (new learning session)
    """
    try:
        progress_data = ProgressService.get_user_progress(current_user.id, sub_link_id)
        
        if not progress_data:
            return jsonify({
                'error': 'No progress found for this subtitle link',
                'code': 'NO_PROGRESS_FOUND'
            }), 404
        
        return jsonify({
            'progress': progress_data
        }), 200
        
    except ProgressServiceError as e:
        error_message = str(e)
        if "not found" in error_message:
            return jsonify({
                'error': error_message,
                'code': 'SUBTITLE_LINK_NOT_FOUND'
            }), 404
        else:
            return jsonify({
                'error': error_message,
                'code': 'PROGRESS_SERVICE_ERROR'
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


@api_bp.route('/progress/<int:sub_link_id>', methods=['PUT'])
@login_required
def update_progress(sub_link_id):
    """
    Update user progress for a specific subtitle link.
    
    Args:
        sub_link_id (int): ID of the subtitle link
        
    Expected JSON payload:
    {
        "current_alignment_index": integer,
        "session_duration_minutes": integer (optional, default 0)
    }
    
    Returns:
        JSON response with updated progress data and statistics
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

        current_alignment_index = data.get('current_alignment_index')
        session_duration_minutes = data.get('session_duration_minutes', 0)

        # Validate required fields
        if current_alignment_index is None:
            return jsonify({
                'error': 'current_alignment_index is required',
                'code': 'MISSING_ALIGNMENT_INDEX'
            }), 400

        # Validate field types and values
        try:
            current_alignment_index = int(current_alignment_index)
            session_duration_minutes = int(session_duration_minutes)

            if current_alignment_index < 0:
                raise ValueError("current_alignment_index must be non-negative")
            if session_duration_minutes < 0:
                raise ValueError("session_duration_minutes must be non-negative")

        except (ValueError, TypeError) as e:
            return jsonify({
                'error': f'Invalid field values: {str(e)}',
                'code': 'INVALID_FIELD_VALUES'
            }), 400

        # Update progress using service layer
        updated_progress = ProgressService.update_progress(
            user_id=current_user.id,
            sub_link_id=sub_link_id,
            current_alignment_index=current_alignment_index,
            session_duration_minutes=session_duration_minutes
        )

        return jsonify({
            'message': 'Progress updated successfully',
            'progress': updated_progress
        }), 200
        
    except ProgressServiceError as e:
        error_message = str(e)
        if "not found" in error_message:
            return jsonify({
                'error': error_message,
                'code': 'SUBTITLE_LINK_NOT_FOUND'
            }), 404
        elif "exceeds total alignments" in error_message or "cannot be negative" in error_message:
            return jsonify({
                'error': error_message,
                'code': 'INVALID_PROGRESS_VALUE'
            }), 400
        else:
            return jsonify({
                'error': error_message,
                'code': 'PROGRESS_SERVICE_ERROR'
            }), 400
            
    except exc.SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            'error': 'Database error occurred while updating progress',
            'code': 'DATABASE_ERROR'
        }), 500
    except Exception:
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500


@api_bp.route('/progress/recent', methods=['GET'])
@login_required
def get_recent_progress():
    """
    Get recently studied subtitle links for current user.
    
    Query parameters:
        limit (int): Maximum number of records to return (default 10, max 50)
        
    Returns:
        JSON response with list of recent progress records
    """
    try:
        # Get limit parameter with validation
        limit = request.args.get('limit', 10)
        try:
            limit = int(limit)
            # Enforce reasonable limits for Pi performance
            if limit < 1:
                limit = 10
            elif limit > 50:
                limit = 50
        except (ValueError, TypeError):
            limit = 10

        recent_progress = ProgressService.get_recent_progress(current_user.id, limit)
        
        return jsonify({
            'recent_progress': recent_progress,
            'count': len(recent_progress)
        }), 200
        
    except ProgressServiceError as e:
        return jsonify({
            'error': str(e),
            'code': 'PROGRESS_SERVICE_ERROR'
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