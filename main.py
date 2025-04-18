from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.api import api_router
from app.middlewares.error_handler import setup_error_handlers
from app.db.init_db import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para la plataforma de gestión de eventos",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

#CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

setup_error_handlers(app)

app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": f"Bienvenido a {settings.PROJECT_NAME}",
        "docs": "/docs",
        "api": settings.API_V1_STR
    }

@app.on_event("startup")
def on_startup():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)