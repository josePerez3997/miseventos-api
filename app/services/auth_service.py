from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.api.dependencies.db import get_database
from app.repositories.user_repository import user_repository
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import Token

class AuthService:
    """
    Service for authentication related operations
    """
    def __init__(self, db: Session = Depends(get_database)):
        self.db = db
    
    def register_new_user(self, user_in: UserCreate) -> User:
        """
        Register a new user
        """
        user = user_repository.get_by_email(self.db, email=user_in.email)
        if user:
            raise ValueError("Email already registered")
        
        user_create_data = {
            "email": user_in.email,
            "password": user_in.password,
            "name": user_in.name,
            "role": getattr(user_in, 'role', "ATTENDEE")
        }
        
        return user_repository.create(self.db, obj_in=UserCreate(**user_create_data))
        
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password
        """
        user = user_repository.authenticate(self.db, email=email, password=password)
        if not user:
            return None
        
        user.last_login = datetime.utcnow()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def create_token_for_user(self, user: User) -> Token:
        """
        Create access token for user
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        return Token(access_token=token, token_type="bearer")
    
    def reset_password(self, email: str) -> bool:
        """
        Initiate password reset process for user
        
        In a real application, this would generate a token and send an email
        For this example, we'll just check if the user exists
        """
        user = user_repository.get_by_email(self.db, email=email)
        if not user:
            return True
        
        return True
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change password for a user
        """
        user = user_repository.get(self.db, id=user_id)
        if not user:
            return False
        
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        self.db.add(user)
        self.db.commit()
        return True