from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.repositories.base import BaseRepository

class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    """
    Repository for Category model
    """
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        """
        Get a category by name (exact match)
        """
        return db.query(Category).filter(Category.name == name).first()

    def search_by_name(self, db: Session, *, name: str) -> List[Category]:
        """
        Search categories by name (partial match)
        """
        return db.query(Category).filter(Category.name.ilike(f"%{name}%")).all()

    def get_categories_by_ids(self, db: Session, *, category_ids: List[int]) -> List[Category]:
        """
        Get multiple categories by their IDs
        """
        return db.query(Category).filter(Category.id.in_(category_ids)).all()

    def get_all_categories(self, db: Session) -> List[Category]:
        """
        Get all categories
        """
        return db.query(Category).all()


category_repository = CategoryRepository(Category)