from fastapi import APIRouter

from app.core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)

@api_router.get("/health-check")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}