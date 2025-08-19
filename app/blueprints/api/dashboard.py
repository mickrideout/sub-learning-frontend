"""Dashboard API endpoints for comprehensive learning analytics."""
from flask import jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import exc
from app.blueprints.api import api_bp
from app import db


@api_bp.route('/progress/dashboard', methods=['GET'])
@login_required
def get_dashboard_stats():
    """
    Get comprehensive learning statistics for dashboard.
    
    Returns:
        JSON response with total study time, completion rates, and analytics
    """
    try:
        from app.services.session_analytics_service import SessionAnalyticsService
        
        # Get comprehensive dashboard statistics
        dashboard_stats = SessionAnalyticsService.get_dashboard_statistics(current_user.id)
        
        return jsonify({
            'stats': dashboard_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error retrieving dashboard statistics',
            'code': 'DASHBOARD_STATS_ERROR'
        }), 500


@api_bp.route('/progress/charts', methods=['GET'])
@login_required
def get_progress_charts():
    """
    Get weekly and monthly progress data for Chart.js visualization.
    
    Query parameters:
        period (str): 'weekly' or 'monthly' (default 'weekly')
        days (int): Number of days back to include (default 30, max 365)
        
    Returns:
        JSON response with chart-ready progress data
    """
    try:
        from app.services.session_analytics_service import SessionAnalyticsService
        
        # Get and validate parameters
        period = request.args.get('period', 'weekly')
        days = request.args.get('days', 30)
        
        try:
            days = int(days)
            if days < 1:
                days = 30
            elif days > 365:  # Pi performance limit
                days = 365
        except (ValueError, TypeError):
            days = 30
            
        if period not in ['weekly', 'monthly']:
            period = 'weekly'
        
        # Get chart data
        chart_data = SessionAnalyticsService.get_progress_chart_data(current_user.id, period, days)
        
        return jsonify({
            'chart_data': chart_data,
            'period': period,
            'days': days
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error retrieving progress charts data',
            'code': 'CHARTS_DATA_ERROR'
        }), 500


@api_bp.route('/progress/streak', methods=['GET'])
@login_required  
def get_learning_streak():
    """
    Get consecutive learning days streak information.
    
    Returns:
        JSON response with current streak, longest streak, and streak history
    """
    try:
        from app.services.session_analytics_service import SessionAnalyticsService
        
        # Calculate streak information
        streak_data = SessionAnalyticsService.calculate_learning_streak(current_user.id)
        
        return jsonify({
            'streak': streak_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error calculating learning streak',
            'code': 'STREAK_CALCULATION_ERROR'
        }), 500


@api_bp.route('/progress/session-history', methods=['GET'])
@login_required
def get_session_history():
    """
    Get detailed session history with movie-language breakdowns.
    
    Query parameters:
        limit (int): Maximum number of sessions to return (default 50, max 100)
        days (int): Number of days back to include (default 30, max 365)
        
    Returns:
        JSON response with session history and analytics
    """
    try:
        from app.services.session_analytics_service import SessionAnalyticsService
        
        # Get and validate parameters
        limit = request.args.get('limit', 50)
        days = request.args.get('days', 30)
        
        try:
            limit = int(limit)
            if limit < 1:
                limit = 50
            elif limit > 100:  # Pi performance limit
                limit = 100
        except (ValueError, TypeError):
            limit = 50
            
        try:
            days = int(days)
            if days < 1:
                days = 30
            elif days > 365:
                days = 365
        except (ValueError, TypeError):
            days = 30
        
        # Get session history
        session_history = SessionAnalyticsService.get_session_history(current_user.id, limit, days)
        
        return jsonify({
            'session_history': session_history,
            'limit': limit,
            'days': days
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error retrieving session history',
            'code': 'SESSION_HISTORY_ERROR'
        }), 500


@api_bp.route('/goals', methods=['POST'])
@login_required
def create_learning_goal():
    """
    Create a new learning goal for the user.
    
    Expected JSON payload:
    {
        "goal_type": "daily_minutes|weekly_alignments|movie_completion",
        "target_value": integer,
        "deadline": "YYYY-MM-DD" (optional)
    }
    
    Returns:
        JSON response with created goal data
    """
    try:
        from app.services.learning_goals_service import LearningGoalsService
        
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
        goal_type = data.get('goal_type')
        target_value = data.get('target_value')
        deadline = data.get('deadline')

        # Validate required fields
        if not goal_type:
            return jsonify({
                'error': 'goal_type is required',
                'code': 'MISSING_GOAL_TYPE'
            }), 400

        if target_value is None:
            return jsonify({
                'error': 'target_value is required',
                'code': 'MISSING_TARGET_VALUE'
            }), 400

        # Create goal using service layer
        new_goal = LearningGoalsService.create_goal(
            user_id=current_user.id,
            goal_type=goal_type,
            target_value=target_value,
            deadline=deadline
        )

        return jsonify({
            'message': 'Learning goal created successfully',
            'goal': new_goal
        }), 201

    except ValueError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Error creating learning goal',
            'code': 'GOAL_CREATION_ERROR'
        }), 500


@api_bp.route('/goals', methods=['GET'])
@login_required
def get_learning_goals():
    """
    Get all learning goals for the current user.
    
    Query parameters:
        active_only (bool): Only return active goals (default true)
        
    Returns:
        JSON response with list of user's learning goals
    """
    try:
        from app.services.learning_goals_service import LearningGoalsService
        
        # Get active_only parameter
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # Get user goals
        goals = LearningGoalsService.get_user_goals(current_user.id, active_only)
        
        return jsonify({
            'goals': goals,
            'count': len(goals),
            'active_only': active_only
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error retrieving learning goals',
            'code': 'GOALS_RETRIEVAL_ERROR'
        }), 500


@api_bp.route('/goals/<int:goal_id>', methods=['PUT'])
@login_required
def update_learning_goal(goal_id):
    """
    Update a learning goal.
    
    Args:
        goal_id (int): ID of the goal to update
        
    Expected JSON payload:
    {
        "target_value": integer (optional),
        "deadline": "YYYY-MM-DD" (optional),
        "is_active": boolean (optional)
    }
    
    Returns:
        JSON response with updated goal data
    """
    try:
        from app.services.learning_goals_service import LearningGoalsService
        
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

        # Update goal using service layer
        updated_goal = LearningGoalsService.update_goal(
            user_id=current_user.id,
            goal_id=goal_id,
            **data
        )

        return jsonify({
            'message': 'Learning goal updated successfully',
            'goal': updated_goal
        }), 200

    except ValueError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Error updating learning goal',
            'code': 'GOAL_UPDATE_ERROR'
        }), 500


@api_bp.route('/goals/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_learning_goal(goal_id):
    """
    Delete a learning goal.
    
    Args:
        goal_id (int): ID of the goal to delete
        
    Returns:
        JSON response confirming deletion
    """
    try:
        from app.services.learning_goals_service import LearningGoalsService
        
        # Delete goal using service layer
        LearningGoalsService.delete_goal(current_user.id, goal_id)
        
        return jsonify({
            'message': 'Learning goal deleted successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Error deleting learning goal',
            'code': 'GOAL_DELETION_ERROR'
        }), 500