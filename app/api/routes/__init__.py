from fastapi import APIRouter

from app.core.config import settings
from app.api.routes import auth, users

api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

@api_router.get("/health-check")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}