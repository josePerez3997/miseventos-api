from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Callable

from app.core.exceptions import MisEventosException

def setup_error_handlers(app: FastAPI) -> None:
    """Setup error handlers for the application"""
    
    @app.exception_handler(MisEventosException)
    async def handle_app_exceptions(request: Request, exc: MisEventosException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def handle_unhandled_exceptions(request: Request, exc: Exception) -> JSONResponse:
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Ocurrió un error inesperado en el servidor."},
        )