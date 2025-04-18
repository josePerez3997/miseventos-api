from fastapi import APIRouter

from app.core.config import settings
from app.api.routes import auth, users, events, speakers, sessions, categories

api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(speakers.router, prefix="/speakers", tags=["speakers"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

@api_router.get("/health-check")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}