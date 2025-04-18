from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_active_user, get_current_active_superuser
from app.models.user import User
from app.services.user_service import UserService
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user
    """
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(),
):
    """
    Update current user
    """
    try:
        user = user_service.update_user(user_id=current_user.id, user_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get("", response_model=List[UserSchema])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(),
):
    """
    Retrieve users (superuser only)
    """
    users = user_service.get_users(skip=skip, limit=limit)
    return users

@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(),
):
    """
    Create new user (superuser only)
    """
    try:
        user = user_service.create_user(user_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(),
):
    """
    Get a specific user by id (superuser only)
    """
    user = user_service.get_user(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(),
):
    """
    Update a user (superuser only)
    """
    try:
        user = user_service.update_user(user_id=user_id, user_in=user_in)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(),
):
    """
    Delete a user (superuser only)
    """
    user = user_service.delete_user(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user