from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import CredentialsException
from app.api.dependencies.db import get_database
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_database),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency that returns the current user based on the JWT token
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise CredentialsException()
    
    user = user_repository.get(db, id=token_data.sub)
    if not user:
        raise CredentialsException()
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that returns the current active user
    """
    if not user_repository.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that returns the current active superuser
    """
    if not user_repository.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def get_optional_current_user(
    db: Session = Depends(get_database),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Dependency that returns the current user or None if not authenticated
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        return None
    
    user = user_repository.get(db, id=token_data.sub)
    if not user:
        return None
    
    if not user_repository.is_active(user):
        return None
    
    return user