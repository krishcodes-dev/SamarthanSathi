"""
Feedback models for training telemetry.
Implements 'Safe Design' (append-only, isolated from core matching).
STRICT SPEC: Separated User and Dispatcher feedback models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.utils.db_types import UUID_STR, generate_uuid

class UserFeedback(Base):
    """
    Telemetry from the reporter/user about extraction accuracy.
    Captured post-extraction, pre-dispatch.
    """
    __tablename__ = "feedback_user"
    
    id = Column(UUID_STR(), primary_key=True, default=generate_uuid)
    request_id = Column(UUID_STR(), ForeignKey("crisis_requests.id"), nullable=False)
    
    # Did we understand the need/location/urgency?
    is_correct = Column(Boolean, nullable=False)
    
    # If not, what was wrong? (e.g. "Not fire, it's a flood")
    corrected_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship (One-way for analysis, not used in live logic)
    request = relationship("CrisisRequest")

class DispatcherFeedback(Base):
    """
    Telemetry from the dispatcher about system performance.
    Captured post-dispatch.
    """
    __tablename__ = "feedback_dispatcher"
    
    id = Column(UUID_STR(), primary_key=True, default=generate_uuid)
    request_id = Column(UUID_STR(), ForeignKey("crisis_requests.id"), nullable=False)
    
    # Ratings (1-5)
    extraction_rating = Column(Integer, nullable=True) # How well did AI extract info?
    matching_rating = Column(Integer, nullable=True)   # How good were the resources?
    
    # Optional qualitative feedback
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    request = relationship("CrisisRequest")
