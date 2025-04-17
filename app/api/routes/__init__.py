from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.api.dependencies.db import get_database

api_router = APIRouter(prefix=settings.API_V1_STR)

@api_router.get("/health-check")
def health_check(db: Session = Depends(get_database)):
    """
    Health check endpoint that verifies database connection
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "Connected"
    except Exception as e:
        db_status = f"Error: {str(e)}"
    
    return {
        "status": "ok",
        "database": db_status
    }