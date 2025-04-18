from sqlalchemy import Boolean, Column, String, Integer, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.db.session import Base
from app.db.base_class import CustomBase

from sqlalchemy.orm import relationship

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ORGANIZER = "ORGANIZER"
    ATTENDEE = "ATTENDEE"

class User(Base, CustomBase):
    """User model"""
    __tablename__ = "users"
    
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ATTENDEE)
    image_url = Column(String(255), nullable=True)

    organized_events = relationship("Event", back_populates="organizer")
    attended_events = relationship("EventAttendee", back_populates="user")
