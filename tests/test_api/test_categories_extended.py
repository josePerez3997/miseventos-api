import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_get_category_by_id(client, test_category, token_headers):
    """Test para obtener una categoría por ID"""
    response = client.get(
        f"{settings.API_V1_STR}/categories/{test_category.id}",
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == test_category.id
    assert response.json()["name"] == test_category.name

def test_update_category(client, test_category, admin_token_headers):
    """Test para actualizar una categoría"""
    update_data = {
        "name": "Updated Category Name",
        "description": "This is an updated category description",
        "color": "#FF5733"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/categories/{test_category.id}",
        json=update_data,
        headers=admin_token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["description"] == update_data["description"]
    assert response.json()["color"] == update_data["color"]

def test_delete_category(client, test_category, admin_token_headers):
    """Test para eliminar una categoría"""
    # Primero aseguramos que no esté asociada a eventos
    test_category.events = []
    
    response = client.delete(
        f"{settings.API_V1_STR}/categories/{test_category.id}",
        headers=admin_token_headers
    )
    
    assert response.status_code == 204
    
    # Verificar que ya no existe
    get_response = client.get(
        f"{settings.API_V1_STR}/categories/{test_category.id}",
        headers=admin_token_headers
    )
    assert get_response.status_code == 404