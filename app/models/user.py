from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.db.session import Base
from app.db.base_class import CustomBase

class UserRole(str, PyEnum):
    ADMIN = "ADMIN"
    ORGANIZER = "ORGANIZER"
    ATTENDEE = "ATTENDEE"

class User(Base, CustomBase):
    """User model"""
    __tablename__ = "users"
    
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    role = Column(SQLAlchemyEnum(UserRole, name="user_role", native_enum=True), 
                 nullable=False, 
                 default=UserRole.ATTENDEE)
                 
    image_url = Column(String(255), nullable=True)
    
    organized_events = relationship("Event", back_populates="organizer")
    attended_events = relationship("EventAttendee", back_populates="user")
    session_attendees = relationship("SessionAttendee", back_populates="user")