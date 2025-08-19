"""Progress service for managing user learning progress."""
from sqlalchemy import exc
from sqlalchemy.orm import exc as orm_exc
from app import db
from app.models.subtitle import UserProgress, SubLink, SubLinkLine


class ProgressServiceError(Exception):
    """Custom exception for progress service errors."""
    pass


class ProgressService:
    """Service class for managing user progress operations."""
    
    @staticmethod
    def get_user_progress(user_id, sub_link_id):
        """
        Get user progress for a specific subtitle link.
        
        Args:
            user_id (int): ID of the user
            sub_link_id (int): ID of the subtitle link
            
        Returns:
            dict: Progress data with completion statistics or None if no progress exists
            
        Raises:
            ProgressServiceError: If validation fails or database error occurs
        """
        try:
            # Validate user owns this progress or sub_link exists
            sub_link = db.session.get(SubLink, sub_link_id)
            if not sub_link:
                raise ProgressServiceError(f"Subtitle link {sub_link_id} not found")
            
            # Get user progress
            progress = UserProgress.query.filter_by(
                user_id=user_id,
                sub_link_id=sub_link_id
            ).first()
            
            if not progress:
                return None
                
            # Get alignment data to calculate completion percentage
            alignment_data = SubLinkLine.query.filter_by(sub_link_id=sub_link_id).first()
            total_alignments = len(alignment_data.link_data) if alignment_data and alignment_data.link_data else 0
            
            # Calculate completion percentage
            completion_percentage = 0.0
            if total_alignments > 0:
                completion_percentage = (progress.current_alignment_index / total_alignments) * 100
                completion_percentage = min(100.0, max(0.0, completion_percentage))
            
            # Return progress with statistics
            progress_dict = progress.to_dict()
            progress_dict['completion_percentage'] = round(completion_percentage, 2)
            progress_dict['total_alignments'] = total_alignments
            
            return progress_dict
            
        except exc.SQLAlchemyError as e:
            raise ProgressServiceError(f"Database error retrieving progress: {str(e)}")
        except Exception as e:
            raise ProgressServiceError(f"Error retrieving progress: {str(e)}")
    
    @staticmethod
    def update_progress(user_id, sub_link_id, current_alignment_index, session_duration_minutes=0):
        """
        Update user progress for a subtitle link.
        
        Args:
            user_id (int): ID of the user
            sub_link_id (int): ID of the subtitle link
            current_alignment_index (int): Current position in alignment array
            session_duration_minutes (int): Minutes spent in current session
            
        Returns:
            dict: Updated progress data with completion statistics
            
        Raises:
            ProgressServiceError: If validation fails or database error occurs
        """
        try:
            # Validate inputs
            if current_alignment_index < 0:
                raise ProgressServiceError("Current alignment index cannot be negative")
            if session_duration_minutes < 0:
                raise ProgressServiceError("Session duration cannot be negative")
                
            # Validate sub_link exists and get total alignments
            sub_link = db.session.get(SubLink, sub_link_id)
            if not sub_link:
                raise ProgressServiceError(f"Subtitle link {sub_link_id} not found")
                
            alignment_data = SubLinkLine.query.filter_by(sub_link_id=sub_link_id).first()
            total_alignments = len(alignment_data.link_data) if alignment_data and alignment_data.link_data else 0
            
            # Validate alignment index is within bounds
            if current_alignment_index > total_alignments:
                raise ProgressServiceError(f"Alignment index {current_alignment_index} exceeds total alignments {total_alignments}")
            
            # Get or create progress record
            progress = UserProgress.query.filter_by(
                user_id=user_id,
                sub_link_id=sub_link_id
            ).first()
            
            if progress:
                # Update existing progress
                progress.current_alignment_index = current_alignment_index
                progress.session_duration_minutes += session_duration_minutes
                progress.last_accessed = db.func.current_timestamp()
                
                # Update total completed alignments (progress made)
                progress.total_alignments_completed = max(progress.total_alignments_completed, current_alignment_index)
            else:
                # Create new progress record
                progress = UserProgress(
                    user_id=user_id,
                    sub_link_id=sub_link_id,
                    current_alignment_index=current_alignment_index,
                    total_alignments_completed=current_alignment_index,
                    session_duration_minutes=session_duration_minutes
                )
                db.session.add(progress)
            
            # Commit changes
            db.session.commit()
            
            # Calculate completion percentage
            completion_percentage = 0.0
            if total_alignments > 0:
                completion_percentage = (progress.current_alignment_index / total_alignments) * 100
                completion_percentage = min(100.0, max(0.0, completion_percentage))
            
            # Return progress with statistics
            progress_dict = progress.to_dict()
            progress_dict['completion_percentage'] = round(completion_percentage, 2)
            progress_dict['total_alignments'] = total_alignments
            
            return progress_dict
                
        except exc.IntegrityError as e:
            db.session.rollback()
            raise ProgressServiceError(f"Progress update constraint violation: {str(e)}")
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise ProgressServiceError(f"Database error updating progress: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ProgressServiceError(f"Error updating progress: {str(e)}")
    
    @staticmethod
    def calculate_completion_percentage(current_index, total_alignments):
        """
        Calculate completion percentage for progress tracking.
        
        Args:
            current_index (int): Current alignment position
            total_alignments (int): Total number of alignments
            
        Returns:
            float: Completion percentage (0.0 to 100.0)
        """
        if total_alignments <= 0:
            return 0.0
        
        percentage = (current_index / total_alignments) * 100
        return round(min(100.0, max(0.0, percentage)), 2)
    
    @staticmethod
    def get_recent_progress(user_id, limit=10):
        """
        Get recently accessed progress sessions for a user.
        
        Args:
            user_id (int): ID of the user
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of recent progress records with completion statistics
            
        Raises:
            ProgressServiceError: If database error occurs
        """
        try:
            progress_records = UserProgress.query.filter_by(
                user_id=user_id
            ).order_by(UserProgress.last_accessed.desc()).limit(limit).all()
            
            result = []
            for progress in progress_records:
                # Get alignment data for completion calculation
                alignment_data = SubLinkLine.query.filter_by(sub_link_id=progress.sub_link_id).first()
                total_alignments = len(alignment_data.link_data) if alignment_data and alignment_data.link_data else 0
                
                # Calculate completion percentage
                completion_percentage = ProgressService.calculate_completion_percentage(
                    progress.current_alignment_index, total_alignments
                )
                
                progress_dict = progress.to_dict()
                progress_dict['completion_percentage'] = completion_percentage
                progress_dict['total_alignments'] = total_alignments
                result.append(progress_dict)
            
            return result
            
        except exc.SQLAlchemyError as e:
            raise ProgressServiceError(f"Database error retrieving recent progress: {str(e)}")
        except Exception as e:
            raise ProgressServiceError(f"Error retrieving recent progress: {str(e)}")