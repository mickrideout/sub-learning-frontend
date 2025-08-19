"""Learning goals service for managing user learning goals."""
from datetime import datetime, date
from sqlalchemy import exc
from app import db
from app.models.learning_goal import LearningGoal


class LearningGoalsServiceError(Exception):
    """Custom exception for learning goals service errors."""
    pass


class LearningGoalsService:
    """Service class for managing learning goals operations."""
    
    VALID_GOAL_TYPES = ['daily_minutes', 'weekly_alignments', 'movie_completion']
    
    @staticmethod
    def create_goal(user_id, goal_type, target_value, deadline=None):
        """
        Create a new learning goal for a user.
        
        Args:
            user_id (int): ID of the user
            goal_type (str): Type of goal (daily_minutes, weekly_alignments, movie_completion)
            target_value (int): Target value to achieve
            deadline (str or date, optional): Goal deadline (YYYY-MM-DD format if string)
            
        Returns:
            dict: Created goal data
            
        Raises:
            ValueError: If validation fails
            LearningGoalsServiceError: If database error occurs
        """
        try:
            # Validate goal type
            if goal_type not in LearningGoalsService.VALID_GOAL_TYPES:
                raise ValueError(f"Invalid goal_type. Must be one of: {LearningGoalsService.VALID_GOAL_TYPES}")
                
            # Validate target value
            try:
                target_value = int(target_value)
                if target_value <= 0:
                    raise ValueError("target_value must be a positive integer")
            except (ValueError, TypeError):
                raise ValueError("target_value must be a positive integer")
                
            # Parse deadline if provided
            deadline_date = None
            if deadline:
                if isinstance(deadline, str):
                    try:
                        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValueError("deadline must be in YYYY-MM-DD format")
                elif isinstance(deadline, date):
                    deadline_date = deadline
                else:
                    raise ValueError("deadline must be a date string or date object")
                    
                # Validate deadline is in future
                if deadline_date <= date.today():
                    raise ValueError("deadline must be in the future")
            
            # Create new goal
            new_goal = LearningGoal(
                user_id=user_id,
                goal_type=goal_type,
                target_value=target_value,
                deadline=deadline_date
            )
            
            db.session.add(new_goal)
            db.session.commit()
            
            return new_goal.to_dict()
            
        except exc.IntegrityError as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Database constraint violation: {str(e)}")
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Database error creating goal: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Error creating goal: {str(e)}")
    
    @staticmethod
    def get_user_goals(user_id, active_only=True):
        """
        Get all learning goals for a user.
        
        Args:
            user_id (int): ID of the user
            active_only (bool): Only return active goals
            
        Returns:
            list: List of goal dictionaries
            
        Raises:
            LearningGoalsServiceError: If database error occurs
        """
        try:
            query = LearningGoal.query.filter_by(user_id=user_id)
            
            if active_only:
                query = query.filter_by(is_active=True)
                
            goals = query.order_by(LearningGoal.created_at.desc()).all()
            
            return [goal.to_dict() for goal in goals]
            
        except exc.SQLAlchemyError as e:
            raise LearningGoalsServiceError(f"Database error retrieving goals: {str(e)}")
        except Exception as e:
            raise LearningGoalsServiceError(f"Error retrieving goals: {str(e)}")
    
    @staticmethod
    def get_goal(user_id, goal_id):
        """
        Get a specific goal for a user.
        
        Args:
            user_id (int): ID of the user
            goal_id (int): ID of the goal
            
        Returns:
            dict: Goal data or None if not found
            
        Raises:
            LearningGoalsServiceError: If database error occurs
        """
        try:
            goal = LearningGoal.query.filter_by(id=goal_id, user_id=user_id).first()
            
            if not goal:
                return None
                
            return goal.to_dict()
            
        except exc.SQLAlchemyError as e:
            raise LearningGoalsServiceError(f"Database error retrieving goal: {str(e)}")
        except Exception as e:
            raise LearningGoalsServiceError(f"Error retrieving goal: {str(e)}")
    
    @staticmethod
    def update_goal(user_id, goal_id, **kwargs):
        """
        Update a learning goal.
        
        Args:
            user_id (int): ID of the user
            goal_id (int): ID of the goal to update
            **kwargs: Fields to update (target_value, deadline, is_active)
            
        Returns:
            dict: Updated goal data
            
        Raises:
            ValueError: If validation fails or goal not found
            LearningGoalsServiceError: If database error occurs
        """
        try:
            # Get goal and validate ownership
            goal = LearningGoal.query.filter_by(id=goal_id, user_id=user_id).first()
            
            if not goal:
                raise ValueError(f"Goal {goal_id} not found for user")
                
            # Update allowed fields
            if 'target_value' in kwargs:
                try:
                    target_value = int(kwargs['target_value'])
                    if target_value <= 0:
                        raise ValueError("target_value must be a positive integer")
                    goal.target_value = target_value
                except (ValueError, TypeError):
                    raise ValueError("target_value must be a positive integer")
                    
            if 'deadline' in kwargs:
                deadline = kwargs['deadline']
                if deadline:
                    if isinstance(deadline, str):
                        try:
                            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
                        except ValueError:
                            raise ValueError("deadline must be in YYYY-MM-DD format")
                    elif isinstance(deadline, date):
                        deadline_date = deadline
                    else:
                        raise ValueError("deadline must be a date string or date object")
                        
                    # Allow updating deadline to past for completed goals
                    goal.deadline = deadline_date
                else:
                    goal.deadline = None
                    
            if 'is_active' in kwargs:
                goal.is_active = bool(kwargs['is_active'])
                
            if 'current_value' in kwargs:
                try:
                    current_value = int(kwargs['current_value'])
                    if current_value < 0:
                        raise ValueError("current_value cannot be negative")
                    goal.update_progress(current_value)
                except (ValueError, TypeError):
                    raise ValueError("current_value must be a non-negative integer")
            
            db.session.commit()
            
            return goal.to_dict()
            
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Database error updating goal: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Error updating goal: {str(e)}")
    
    @staticmethod
    def delete_goal(user_id, goal_id):
        """
        Delete a learning goal.
        
        Args:
            user_id (int): ID of the user
            goal_id (int): ID of the goal to delete
            
        Raises:
            ValueError: If goal not found
            LearningGoalsServiceError: If database error occurs
        """
        try:
            # Get goal and validate ownership
            goal = LearningGoal.query.filter_by(id=goal_id, user_id=user_id).first()
            
            if not goal:
                raise ValueError(f"Goal {goal_id} not found for user")
            
            db.session.delete(goal)
            db.session.commit()
            
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Database error deleting goal: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Error deleting goal: {str(e)}")
    
    @staticmethod
    def update_goal_progress(user_id, goal_type, progress_amount):
        """
        Update progress for all active goals of a specific type.
        
        Args:
            user_id (int): ID of the user
            goal_type (str): Type of goals to update
            progress_amount (int): Amount of progress to add
            
        Returns:
            list: List of updated goals that were affected
            
        Raises:
            LearningGoalsServiceError: If database error occurs
        """
        try:
            # Get all active goals of this type for user
            goals = LearningGoal.query.filter_by(
                user_id=user_id,
                goal_type=goal_type,
                is_active=True
            ).all()
            
            updated_goals = []
            
            for goal in goals:
                goal.increment_progress(progress_amount)
                updated_goals.append(goal.to_dict())
            
            if updated_goals:
                db.session.commit()
                
            return updated_goals
            
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Database error updating goal progress: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Error updating goal progress: {str(e)}")
    
    @staticmethod
    def check_goal_completion(user_id):
        """
        Check for newly completed goals and return achievement data.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            list: List of newly completed goals
            
        Raises:
            LearningGoalsServiceError: If database error occurs
        """
        try:
            # Find goals that are completed but don't have completed_at timestamp
            newly_completed = LearningGoal.query.filter(
                LearningGoal.user_id == user_id,
                LearningGoal.is_active == True,
                LearningGoal.current_value >= LearningGoal.target_value,
                LearningGoal.completed_at == None
            ).all()
            
            achievements = []
            for goal in newly_completed:
                goal.completed_at = datetime.utcnow()
                achievements.append(goal.to_dict())
            
            if achievements:
                db.session.commit()
                
            return achievements
            
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Database error checking goal completion: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise LearningGoalsServiceError(f"Error checking goal completion: {str(e)}")
    
    @staticmethod
    def get_goal_statistics(user_id):
        """
        Get overall goal statistics for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            dict: Goal statistics including completion rates
            
        Raises:
            LearningGoalsServiceError: If database error occurs
        """
        try:
            goals = LearningGoal.query.filter_by(user_id=user_id).all()
            
            if not goals:
                return {
                    'total_goals': 0,
                    'completed_goals': 0,
                    'active_goals': 0,
                    'completion_rate': 0.0,
                    'overdue_goals': 0,
                    'goals_by_type': {}
                }
            
            completed = len([g for g in goals if g.is_goal_completed()])
            active = len([g for g in goals if g.is_active])
            overdue = len([g for g in goals if g.is_overdue()])
            
            # Group by goal type
            goals_by_type = {}
            for goal in goals:
                if goal.goal_type not in goals_by_type:
                    goals_by_type[goal.goal_type] = {'total': 0, 'completed': 0}
                goals_by_type[goal.goal_type]['total'] += 1
                if goal.is_goal_completed():
                    goals_by_type[goal.goal_type]['completed'] += 1
            
            completion_rate = (completed / len(goals)) * 100 if goals else 0.0
            
            return {
                'total_goals': len(goals),
                'completed_goals': completed,
                'active_goals': active,
                'completion_rate': round(completion_rate, 2),
                'overdue_goals': overdue,
                'goals_by_type': goals_by_type
            }
            
        except exc.SQLAlchemyError as e:
            raise LearningGoalsServiceError(f"Database error retrieving goal statistics: {str(e)}")
        except Exception as e:
            raise LearningGoalsServiceError(f"Error retrieving goal statistics: {str(e)}")