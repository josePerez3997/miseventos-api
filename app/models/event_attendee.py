from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.db.base_class import CustomBase

class EventAttendee(Base, CustomBase):
    """Model for event-attendee relationship"""
    __tablename__ = "event_attendees"
    
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    event = relationship("Event", back_populates="attendees")
    user = relationship("User", back_populates="attended_events")
    
    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', name='unique_event_user'),
    )