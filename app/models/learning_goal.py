"""Learning goal model for user goal tracking and motivation."""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app import db


class LearningGoal(db.Model):
    """
    Model for user learning goals with progress tracking.
    
    Supports different goal types:
    - daily_minutes: Daily study time target
    - weekly_alignments: Weekly alignments completion target
    - movie_completion: Complete specific number of movies
    """
    __tablename__ = 'learning_goals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    goal_type = Column(String(50), nullable=False)
    target_value = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0, nullable=False)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to user
    user = relationship('User', backref='learning_goals')
    
    def __init__(self, user_id, goal_type, target_value, deadline=None):
        """
        Initialize a new learning goal.
        
        Args:
            user_id (int): ID of the user who owns this goal
            goal_type (str): Type of goal (daily_minutes, weekly_alignments, movie_completion)
            target_value (int): Target value to achieve
            deadline (date, optional): Goal completion deadline
        """
        self.user_id = user_id
        self.goal_type = goal_type
        self.target_value = target_value
        self.deadline = deadline
        self.current_value = 0
        self.is_active = True
        self.created_at = datetime.utcnow()
        
    def to_dict(self):
        """
        Convert goal to dictionary for JSON serialization.
        
        Returns:
            dict: Goal data with progress calculation
        """
        progress_percentage = 0.0
        if self.target_value > 0:
            progress_percentage = min(100.0, (self.current_value / self.target_value) * 100)
            
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_type': self.goal_type,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'progress_percentage': round(progress_percentage, 2),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_active': self.is_active,
            'is_completed': self.current_value >= self.target_value
        }
        
    def update_progress(self, new_value):
        """
        Update goal progress and check for completion.
        
        Args:
            new_value (int): New progress value
        """
        self.current_value = max(0, new_value)
        
        # Check if goal is completed
        if self.current_value >= self.target_value and not self.completed_at:
            self.completed_at = datetime.utcnow()
            
    def increment_progress(self, amount=1):
        """
        Increment goal progress by specified amount.
        
        Args:
            amount (int): Amount to add to current progress
        """
        self.update_progress(self.current_value + amount)
        
    def is_goal_completed(self):
        """
        Check if goal has been completed.
        
        Returns:
            bool: True if goal is completed
        """
        return self.current_value >= self.target_value
        
    def days_until_deadline(self):
        """
        Calculate days remaining until deadline.
        
        Returns:
            int: Days until deadline, None if no deadline set, negative if overdue
        """
        if not self.deadline:
            return None
            
        today = date.today()
        delta = self.deadline - today
        return delta.days
        
    def is_overdue(self):
        """
        Check if goal is overdue.
        
        Returns:
            bool: True if goal has passed deadline without completion
        """
        if not self.deadline:
            return False
            
        return date.today() > self.deadline and not self.is_goal_completed()
        
    def get_progress_rate(self):
        """
        Calculate daily progress rate needed to meet deadline.
        
        Returns:
            float: Required daily progress rate, None if no deadline
        """
        days_remaining = self.days_until_deadline()
        if days_remaining is None or days_remaining <= 0:
            return None
            
        remaining_progress = max(0, self.target_value - self.current_value)
        return remaining_progress / days_remaining
        
    def __repr__(self):
        """String representation of the learning goal."""
        return f'<LearningGoal {self.id}: {self.goal_type} - {self.current_value}/{self.target_value}>'