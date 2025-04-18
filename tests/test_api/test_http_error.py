import pytest
from fastapi import Request, status
from app.api.errors.http_error import http_error_handler

async def test_http_error_handler():
    """Test para el manejador de errores HTTP"""
    class MockException:
        status_code = status.HTTP_404_NOT_FOUND
        detail = "Test error detail"
    
    request = Request({"type": "http", "query_string": b"", "headers": [], "path": "/"})
    
    response = await http_error_handler(request, MockException())
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.body == b'{"detail":"Test error detail"}'