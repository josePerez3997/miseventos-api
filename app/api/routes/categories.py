from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user, get_current_active_superuser
from app.models.user import User
from app.services.category_service import CategoryService
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithEvents

router = APIRouter()

@router.get("", response_model=List[Category])
def get_categories(
    name: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_service: CategoryService = Depends(),
):
    """
    Get all categories with optional name filter
    """
    if name:
        categories = category_service.search_categories(name=name)
    else:
        categories = category_service.get_categories(skip=skip, limit=limit)
    
    return categories

@router.get("/all", response_model=List[Category])
def get_all_categories(
    category_service: CategoryService = Depends(),
):
    """
    Get all categories without pagination
    """
    return category_service.get_all_categories()

@router.get("/stats", response_model=List[Dict])
def get_category_stats(
    category_service: CategoryService = Depends(),
):
    """
    Get statistics about categories (count of events per category)
    """
    return category_service.get_category_stats()

@router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_superuser),
    category_service: CategoryService = Depends(),
):
    """
    Create a new category (admin only)
    """
    try:
        category = category_service.create_category(category_in=category_in)
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get("/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    category_service: CategoryService = Depends(),
):
    """
    Get a specific category by ID
    """
    category = category_service.get_category(category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return category

@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_active_superuser),
    category_service: CategoryService = Depends(),
):
    """
    Update a category (admin only)
    """
    try:
        category = category_service.update_category(
            category_id=category_id, 
            category_in=category_in
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_superuser),
    category_service: CategoryService = Depends(),
):
    """
    Delete a category if not used in any events (admin only)
    """
    try:
        success = category_service.delete_category(category_id=category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return None
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )