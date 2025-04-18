from typing import List, Optional, Dict

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_database
from app.repositories.category_repository import category_repository
from app.repositories.event_repository import event_repository
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    """
    Service for category related operations
    """
    def __init__(self, db: Session = Depends(get_database)):
        self.db = db
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """
        Get a category by ID
        """
        return category_repository.get(self.db, id=category_id)
    
    def get_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """
        Get all categories with pagination
        """
        return category_repository.get_multi(self.db, skip=skip, limit=limit)
    
    def get_all_categories(self) -> List[Category]:
        """
        Get all categories without pagination
        """
        return category_repository.get_all_categories(self.db)
    
    def get_categories_by_ids(self, category_ids: List[int]) -> List[Category]:
        """
        Get multiple categories by their IDs
        """
        return category_repository.get_categories_by_ids(self.db, category_ids=category_ids)
    
    def search_categories(self, name: str) -> List[Category]:
        """
        Search categories by name
        """
        return category_repository.search_by_name(self.db, name=name)
    
    def create_category(self, category_in: CategoryCreate) -> Category:
        """
        Create a new category
        """
        existing = category_repository.get_by_name(self.db, name=category_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists",
            )
        
        return category_repository.create(self.db, obj_in=category_in)
    
    def update_category(self, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
        """
        Update a category
        """
        category = self.get_category(category_id)
        if not category:
            return None
        
        if category_in.name and category_in.name != category.name:
            existing = category_repository.get_by_name(self.db, name=category_in.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists",
                )
        
        return category_repository.update(self.db, db_obj=category, obj_in=category_in)
    
    def delete_category(self, category_id: int) -> bool:
        """
        Delete a category if not used in any events
        """
        category = self.get_category(category_id)
        if not category:
            return False
        
        events = event_repository.get_events_by_category(self.db, category_id=category_id)
        if events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category because it is used in {len(events)} events",
            )
        
        category_repository.remove(self.db, id=category_id)
        return True
    
    def get_category_stats(self) -> List[Dict]:
        """
        Get statistics about categories (count of events per category)
        """
        categories = self.get_all_categories()
        result = []
        
        for category in categories:
            events = event_repository.get_events_by_category(self.db, category_id=category.id)
            result.append({
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "event_count": len(events)
            })
        
        return result