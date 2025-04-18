from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.db.session import Base
from app.db.base_class import CustomBase

class EventStatus(str, PyEnum):
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Event(Base, CustomBase):
    """Event model"""
    __tablename__ = "events"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=False)
    date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    capacity = Column(Integer, nullable=False)
    registered_attendees = Column(Integer, default=0)
    
    status = Column(SQLAlchemyEnum(EventStatus, name="event_status", native_enum=True), 
                   nullable=False, 
                   default=EventStatus.UPCOMING)
                   
    image_url = Column(String(255), nullable=True)
    
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    organizer = relationship("User", back_populates="organized_events")
    sessions = relationship("Session", back_populates="event", cascade="all, delete-orphan")
    attendees = relationship("EventAttendee", back_populates="event", cascade="all, delete-orphan")