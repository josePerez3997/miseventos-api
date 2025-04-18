from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.base_class import CustomBase

class Session(Base, CustomBase):
    """Session model"""
    __tablename__ = "sessions"

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    speaker_id = Column(Integer, ForeignKey("speakers.id", ondelete="RESTRICT"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=False)
    registered_attendees = Column(Integer, default=0)

    event = relationship("Event", back_populates="sessions")
    speaker = relationship("Speaker", back_populates="sessions")
    attendees = relationship("SessionAttendee", back_populates="session", cascade="all, delete-orphan")