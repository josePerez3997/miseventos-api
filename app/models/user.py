from sqlalchemy import Boolean, Column, String, Integer, DateTime
from sqlalchemy.sql import func

from app.db.session import Base
from app.db.base_class import CustomBase

class User(Base, CustomBase):
    """User model"""
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Roles: 1 = Admin, 2 = Organizer, 3 = Attendee
    role = Column(Integer, default=3) 
    
    phone = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)