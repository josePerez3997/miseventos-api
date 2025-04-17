from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

from app.db.session import Base

class BaseModel(object):
    """Base model for all database models"""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())