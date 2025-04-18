from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.db.base_class import CustomBase

class SessionAttendee(Base, CustomBase):
    """Model for session-attendee relationship"""
    __tablename__ = "session_attendees"
    
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("Session", back_populates="attendees")
    user = relationship("User", back_populates="session_attendees")
    
    __table_args__ = (
        UniqueConstraint('session_id', 'user_id', name='unique_session_user'),
    )