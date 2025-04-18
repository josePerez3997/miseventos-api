from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.base_class import CustomBase

class Speaker(Base, CustomBase):
    """Speaker model"""
    __tablename__ = "speakers"

    name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)

    sessions = relationship("Session", back_populates="speaker")