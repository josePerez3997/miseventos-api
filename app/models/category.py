from sqlalchemy import Column, String, Table, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.base_class import CustomBase

event_category = Table(
    "event_categories",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
)

class Category(Base, CustomBase):
    """Category model"""
    __tablename__ = "categories"

    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(200), nullable=True)
    color = Column(String(20), nullable=True)  

    events = relationship("Event", secondary=event_category, back_populates="categories")

    def __repr__(self):
        return f"<Category {self.name}>"