from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_database
from app.repositories.user_repository import user_repository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    """
    Service for user related operations
    """
    def __init__(self, db: Session = Depends(get_database)):
        self.db = db
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID
        """
        return user_repository.get(self.db, id=user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        """
        return user_repository.get_by_email(self.db, email=email)
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get a list of users
        """
        return user_repository.get_multi(self.db, skip=skip, limit=limit)
    
    def create_user(self, user_in: UserCreate) -> User:
        """
        Create a new user
        """
        user = self.get_user_by_email(email=user_in.email)
        if user:
            raise ValueError("Email already registered")
        
        return user_repository.create(self.db, obj_in=user_in)
    
    def update_user(self, user_id: int, user_in: UserUpdate) -> Optional[User]:
        """
        Update a user
        """
        user = self.get_user(user_id=user_id)
        if not user:
            return None
        
        if user_in.email and user_in.email != user.email:
            existing_user = self.get_user_by_email(email=user_in.email)
            if existing_user:
                raise ValueError("Email already registered")
        
        return user_repository.update(self.db, db_obj=user, obj_in=user_in)
    
    def delete_user(self, user_id: int) -> Optional[User]:
        """
        Delete a user
        """
        user = self.get_user(user_id=user_id)
        if not user:
            return None
        
        return user_repository.remove(self.db, id=user_id)
    
    def is_active(self, user: User) -> bool:
        """
        Check if user is active
        """
        return user_repository.is_active(user)
    
    def is_superuser(self, user: User) -> bool:
        """
        Check if user is superuser
        """
        return user_repository.is_superuser(user)