import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_get_categories(client, token_headers):
    """Test para obtener categorías"""
    response = client.get(f"{settings.API_V1_STR}/categories", headers=token_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_all_categories(client, token_headers):
    """Test para obtener todas las categorías sin paginación"""
    response = client.get(f"{settings.API_V1_STR}/categories/all", headers=token_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_category_stats(client, token_headers):
    """Test para obtener estadísticas de categorías"""
    response = client.get(f"{settings.API_V1_STR}/categories/stats", headers=token_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_category(client, admin_token_headers):
    """Test para crear una categoría"""
    category_data = {
        "name": "New API Test Category",
        "description": "This is a category created via API test",
        "color": "#FF5733"
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/categories", 
        json=category_data, 
        headers=admin_token_headers
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == category_data["name"]
    assert response.json()["description"] == category_data["description"]
    assert response.json()["color"] == category_data["color"]