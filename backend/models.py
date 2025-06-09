from sqlalchemy import Column, String, JSON, DateTime, BigInteger, Text, Integer
from datetime import datetime
import uuid

from .database import Base

class Task(Base):
    """
    AI Task model combining Claude architecture with DeepSeek implementation
    """
    __tablename__ = "ai_tasks"

    # Primary key - using string UUID for better scalability (Claude approach)
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Core task fields
    assignee = Column(String, nullable=False, index=True)  # 'claude', 'deepseek', 'grok'
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # DeepSeek addition for detailed descriptions
    status = Column(String(20), nullable=False, default="pending", index=True)  # DeepSeek typing
    
    # User and tracking fields
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # JSON data fields (Claude flexible approach)
    input_data = Column(JSON, nullable=False, default=dict)  # Task input data
    output_data = Column(JSON, nullable=True)  # Task results
    
    # User tracking (DeepSeek approach + Claude Telegram integration)
    user_id = Column(BigInteger, nullable=True, index=True)  # Telegram user ID
    telegram_chat_id = Column(BigInteger, nullable=False, index=True)  # Chat context
    
    # Timestamps (both approaches)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Additional metadata
    priority = Column(String(10), default="normal")  # Claude enhancement
    estimated_duration = Column(Integer, nullable=True)  # Minutes
    actual_duration = Column(Integer, nullable=True)  # Minutes
    
    def __repr__(self):
        return f"<Task(id={self.id}, assignee={self.assignee}, status={self.status}, title='{self.title[:50]}')>"
    
    @property
    def is_pending(self):
        return self.status == "pending"
    
    @property
    def is_completed(self):
        return self.status == "completed"
    
    @property
    def duration_minutes(self):
        """Calculate task duration if completed"""
        if self.completed_at and self.created_at:
            delta = self.completed_at - self.created_at
            return int(delta.total_seconds() / 60)
        return None