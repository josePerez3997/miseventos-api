from fastapi import Request, status
from fastapi.responses import JSONResponse

async def http_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )