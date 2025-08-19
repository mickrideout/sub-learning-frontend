"""Session analytics service for comprehensive learning analytics and insights."""
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc, and_, or_
from sqlalchemy import exc
from app import db
from app.models.subtitle import UserProgress, SubLink
from app.models.user import User


class SessionAnalyticsServiceError(Exception):
    """Custom exception for session analytics service errors."""
    pass


class SessionAnalyticsService:
    """Service class for session analytics and learning insights."""
    
    @staticmethod
    def get_dashboard_statistics(user_id):
        """
        Get comprehensive dashboard statistics for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            dict: Comprehensive dashboard statistics
            
        Raises:
            SessionAnalyticsServiceError: If database error occurs
        """
        try:
            # Get all user progress records
            progress_records = UserProgress.query.filter_by(user_id=user_id).all()
            
            if not progress_records:
                return {
                    'total_study_minutes': 0,
                    'movies_completed': 0,
                    'total_alignments': 0,
                    'current_streak': 0,
                    'completion_rate': 0.0,
                    'avg_session_duration': 0.0,
                    'learning_velocity': 0.0,
                    'active_sessions': 0,
                    'total_sessions': 0
                }
            
            # Calculate basic statistics
            total_study_minutes = sum(p.session_duration_minutes for p in progress_records)
            total_alignments = sum(p.total_alignments_completed for p in progress_records)
            
            # Count movies (completed defined as > 80% completion)
            movies_completed = 0
            active_sessions = 0
            total_sessions = len(progress_records)
            
            for progress in progress_records:
                # Get total alignments for this subtitle link
                sub_link_line = db.session.query(db.func.length(
                    db.session.query(func.json_extract(
                        db.select([func.json_array_length(
                            func.json_extract(
                                db.select([func.coalesce(
                                    func.json_extract(
                                        db.select([func.coalesce(func.json('[]'), func.json('[]'))]).scalar(),
                                        '$'
                                    ), 
                                    func.json('[]')
                                )]).scalar(), '$'
                            )
                        )]).scalar()
                    )).scalar()
                )).scalar()
                
                # Simplified approach - just check if user has made significant progress
                if progress.current_alignment_index > 0:
                    active_sessions += 1
                    
                # Consider completed if substantial progress made (this is simplified)
                if progress.total_alignments_completed > 50:  # Arbitrary threshold
                    movies_completed += 1
            
            # Calculate averages
            avg_session_duration = total_study_minutes / total_sessions if total_sessions > 0 else 0.0
            completion_rate = (movies_completed / total_sessions) * 100 if total_sessions > 0 else 0.0
            learning_velocity = total_alignments / (total_study_minutes / 60) if total_study_minutes > 0 else 0.0
            
            # Get current streak
            current_streak = SessionAnalyticsService.calculate_learning_streak(user_id)['current_streak']
            
            return {
                'total_study_minutes': total_study_minutes,
                'movies_completed': movies_completed,
                'total_alignments': total_alignments,
                'current_streak': current_streak,
                'completion_rate': round(completion_rate, 2),
                'avg_session_duration': round(avg_session_duration, 2),
                'learning_velocity': round(learning_velocity, 2),  # alignments per hour
                'active_sessions': active_sessions,
                'total_sessions': total_sessions
            }
            
        except exc.SQLAlchemyError as e:
            raise SessionAnalyticsServiceError(f"Database error retrieving dashboard statistics: {str(e)}")
        except Exception as e:
            raise SessionAnalyticsServiceError(f"Error retrieving dashboard statistics: {str(e)}")
    
    @staticmethod
    def get_progress_chart_data(user_id, period='weekly', days=30):
        """
        Get progress chart data for visualization.
        
        Args:
            user_id (int): ID of the user
            period (str): 'weekly' or 'monthly'
            days (int): Number of days back to include
            
        Returns:
            dict: Chart-ready data with labels and datasets
            
        Raises:
            SessionAnalyticsServiceError: If database error occurs
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get progress records within date range
            progress_records = UserProgress.query.filter(
                UserProgress.user_id == user_id,
                UserProgress.last_accessed >= start_date,
                UserProgress.last_accessed <= end_date
            ).order_by(UserProgress.last_accessed).all()
            
            # Group data by period
            if period == 'weekly':
                chart_data = SessionAnalyticsService._group_data_weekly(progress_records, start_date, end_date)
            else:  # monthly
                chart_data = SessionAnalyticsService._group_data_monthly(progress_records, start_date, end_date)
            
            return chart_data
            
        except exc.SQLAlchemyError as e:
            raise SessionAnalyticsServiceError(f"Database error retrieving chart data: {str(e)}")
        except Exception as e:
            raise SessionAnalyticsServiceError(f"Error retrieving chart data: {str(e)}")
    
    @staticmethod
    def _group_data_weekly(progress_records, start_date, end_date):
        """Group progress data by week for chart visualization."""
        # Create weekly buckets
        weekly_data = {}
        current_date = start_date
        
        while current_date <= end_date:
            week_start = current_date - timedelta(days=current_date.weekday())
            week_key = week_start.strftime('%Y-W%U')
            week_label = week_start.strftime('%b %d')
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    'label': week_label,
                    'study_minutes': 0,
                    'alignments_completed': 0,
                    'sessions': 0
                }
            
            current_date += timedelta(days=7)
        
        # Populate data
        for progress in progress_records:
            progress_date = progress.last_accessed.date()
            week_start = progress_date - timedelta(days=progress_date.weekday())
            week_key = week_start.strftime('%Y-W%U')
            
            if week_key in weekly_data:
                weekly_data[week_key]['study_minutes'] += progress.session_duration_minutes
                weekly_data[week_key]['alignments_completed'] += progress.total_alignments_completed
                weekly_data[week_key]['sessions'] += 1
        
        # Convert to chart format
        labels = []
        study_data = []
        alignment_data = []
        
        for week_key in sorted(weekly_data.keys()):
            data = weekly_data[week_key]
            labels.append(data['label'])
            study_data.append(data['study_minutes'])
            alignment_data.append(data['alignments_completed'])
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Study Minutes',
                    'data': study_data,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                },
                {
                    'label': 'Alignments Completed',
                    'data': alignment_data,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                }
            ]
        }
    
    @staticmethod
    def _group_data_monthly(progress_records, start_date, end_date):
        """Group progress data by month for chart visualization."""
        monthly_data = {}
        
        # Create monthly buckets
        current_date = start_date.replace(day=1)  # First day of start month
        
        while current_date <= end_date:
            month_key = current_date.strftime('%Y-%m')
            month_label = current_date.strftime('%b %Y')
            
            monthly_data[month_key] = {
                'label': month_label,
                'study_minutes': 0,
                'alignments_completed': 0,
                'sessions': 0
            }
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Populate data
        for progress in progress_records:
            month_key = progress.last_accessed.strftime('%Y-%m')
            
            if month_key in monthly_data:
                monthly_data[month_key]['study_minutes'] += progress.session_duration_minutes
                monthly_data[month_key]['alignments_completed'] += progress.total_alignments_completed
                monthly_data[month_key]['sessions'] += 1
        
        # Convert to chart format
        labels = []
        study_data = []
        alignment_data = []
        
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            labels.append(data['label'])
            study_data.append(data['study_minutes'])
            alignment_data.append(data['alignments_completed'])
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Study Minutes',
                    'data': study_data,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                },
                {
                    'label': 'Alignments Completed',
                    'data': alignment_data,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                }
            ]
        }
    
    @staticmethod
    def calculate_learning_streak(user_id):
        """
        Calculate consecutive learning days streak.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            dict: Streak information including current and longest streaks
            
        Raises:
            SessionAnalyticsServiceError: If database error occurs
        """
        try:
            # Get all progress records ordered by date
            progress_records = UserProgress.query.filter_by(
                user_id=user_id
            ).order_by(desc(UserProgress.last_accessed)).all()
            
            if not progress_records:
                return {
                    'current_streak': 0,
                    'longest_streak': 0,
                    'last_activity_date': None,
                    'streak_start_date': None
                }
            
            # Get unique activity dates
            activity_dates = set()
            for progress in progress_records:
                activity_dates.add(progress.last_accessed.date())
            
            activity_dates = sorted(activity_dates, reverse=True)
            
            # Calculate current streak
            current_streak = 0
            today = date.today()
            
            # Check if user studied today or yesterday (allow for timezone flexibility)
            if activity_dates[0] >= today - timedelta(days=1):
                current_date = activity_dates[0]
                current_streak = 1
                
                # Count consecutive days backwards
                for i in range(1, len(activity_dates)):
                    expected_date = current_date - timedelta(days=i)
                    if activity_dates[i] == expected_date:
                        current_streak += 1
                    else:
                        break
            
            # Calculate longest streak
            longest_streak = 0
            temp_streak = 1
            
            for i in range(1, len(activity_dates)):
                if activity_dates[i-1] - activity_dates[i] == timedelta(days=1):
                    temp_streak += 1
                else:
                    longest_streak = max(longest_streak, temp_streak)
                    temp_streak = 1
            
            longest_streak = max(longest_streak, temp_streak)
            
            # Get streak start date
            streak_start_date = None
            if current_streak > 0 and activity_dates:
                streak_start_date = activity_dates[min(current_streak - 1, len(activity_dates) - 1)]
            
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'last_activity_date': activity_dates[0].isoformat() if activity_dates else None,
                'streak_start_date': streak_start_date.isoformat() if streak_start_date else None
            }
            
        except exc.SQLAlchemyError as e:
            raise SessionAnalyticsServiceError(f"Database error calculating streak: {str(e)}")
        except Exception as e:
            raise SessionAnalyticsServiceError(f"Error calculating streak: {str(e)}")
    
    @staticmethod
    def get_session_history(user_id, limit=50, days=30):
        """
        Get detailed session history with movie-language breakdowns.
        
        Args:
            user_id (int): ID of the user
            limit (int): Maximum number of sessions to return
            days (int): Number of days back to include
            
        Returns:
            list: List of session history entries
            
        Raises:
            SessionAnalyticsServiceError: If database error occurs
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get progress records with subtitle link information
            progress_records = db.session.query(
                UserProgress, SubLink
            ).join(
                SubLink, UserProgress.sub_link_id == SubLink.id
            ).filter(
                UserProgress.user_id == user_id,
                UserProgress.last_accessed >= start_date,
                UserProgress.last_accessed <= end_date
            ).order_by(
                desc(UserProgress.last_accessed)
            ).limit(limit).all()
            
            session_history = []
            
            for progress, sub_link in progress_records:
                # Parse language pair from sub_link data if available
                language_pair = "Unknown"
                movie_title = f"Movie ID: {sub_link.id}"
                
                # Try to extract movie title and language info from sub_link
                # This is a simplified version - actual implementation would depend on data structure
                
                session_entry = {
                    'date': progress.last_accessed.strftime('%Y-%m-%d'),
                    'datetime': progress.last_accessed.isoformat(),
                    'movie_title': movie_title,
                    'language_pair': language_pair,
                    'duration_minutes': progress.session_duration_minutes,
                    'alignments_studied': progress.total_alignments_completed,
                    'current_position': progress.current_alignment_index,
                    'sub_link_id': sub_link.id,
                    'progress_percentage': SessionAnalyticsService._calculate_progress_percentage(
                        progress.current_alignment_index, sub_link.id
                    )
                }
                
                session_history.append(session_entry)
            
            return session_history
            
        except exc.SQLAlchemyError as e:
            raise SessionAnalyticsServiceError(f"Database error retrieving session history: {str(e)}")
        except Exception as e:
            raise SessionAnalyticsServiceError(f"Error retrieving session history: {str(e)}")
    
    @staticmethod
    def _calculate_progress_percentage(current_index, sub_link_id):
        """Calculate progress percentage for a subtitle link."""
        try:
            from app.models.subtitle import SubLinkLine
            
            # Get alignment data
            alignment_data = SubLinkLine.query.filter_by(sub_link_id=sub_link_id).first()
            if not alignment_data or not alignment_data.link_data:
                return 0.0
            
            total_alignments = len(alignment_data.link_data)
            if total_alignments == 0:
                return 0.0
            
            percentage = (current_index / total_alignments) * 100
            return round(min(100.0, max(0.0, percentage)), 2)
            
        except Exception:
            return 0.0
    
    @staticmethod
    def get_learning_velocity_trends(user_id, days=30):
        """
        Calculate learning velocity trends (alignments per hour over time).
        
        Args:
            user_id (int): ID of the user
            days (int): Number of days to analyze
            
        Returns:
            dict: Velocity trend data
            
        Raises:
            SessionAnalyticsServiceError: If database error occurs
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get progress records within date range
            progress_records = UserProgress.query.filter(
                UserProgress.user_id == user_id,
                UserProgress.last_accessed >= start_date,
                UserProgress.last_accessed <= end_date
            ).order_by(UserProgress.last_accessed).all()
            
            if not progress_records:
                return {
                    'daily_velocities': [],
                    'average_velocity': 0.0,
                    'trend': 'stable'
                }
            
            # Group by day and calculate daily velocities
            daily_data = {}
            
            for progress in progress_records:
                day_key = progress.last_accessed.date()
                
                if day_key not in daily_data:
                    daily_data[day_key] = {
                        'total_alignments': 0,
                        'total_minutes': 0
                    }
                
                daily_data[day_key]['total_alignments'] += progress.total_alignments_completed
                daily_data[day_key]['total_minutes'] += progress.session_duration_minutes
            
            # Calculate daily velocities
            daily_velocities = []
            for day, data in sorted(daily_data.items()):
                velocity = 0.0
                if data['total_minutes'] > 0:
                    velocity = data['total_alignments'] / (data['total_minutes'] / 60)
                
                daily_velocities.append({
                    'date': day.isoformat(),
                    'velocity': round(velocity, 2),
                    'alignments': data['total_alignments'],
                    'minutes': data['total_minutes']
                })
            
            # Calculate average velocity
            velocities = [d['velocity'] for d in daily_velocities if d['velocity'] > 0]
            average_velocity = sum(velocities) / len(velocities) if velocities else 0.0
            
            # Determine trend (simplified)
            trend = 'stable'
            if len(velocities) >= 3:
                recent_avg = sum(velocities[-3:]) / 3
                older_avg = sum(velocities[:-3]) / len(velocities[:-3]) if len(velocities) > 3 else recent_avg
                
                if recent_avg > older_avg * 1.1:
                    trend = 'improving'
                elif recent_avg < older_avg * 0.9:
                    trend = 'declining'
            
            return {
                'daily_velocities': daily_velocities,
                'average_velocity': round(average_velocity, 2),
                'trend': trend
            }
            
        except exc.SQLAlchemyError as e:
            raise SessionAnalyticsServiceError(f"Database error calculating velocity trends: {str(e)}")
        except Exception as e:
            raise SessionAnalyticsServiceError(f"Error calculating velocity trends: {str(e)}")