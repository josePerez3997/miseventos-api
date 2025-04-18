import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_get_speakers(client, token_headers):
    """Test para obtener ponentes"""
    response = client.get(f"{settings.API_V1_STR}/speakers", headers=token_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_speaker(client, token_headers):
    """Test para crear un ponente"""
    speaker_data = {
        "name": "New Test Speaker",
        "bio": "This is a test speaker with sufficient length bio created via API test"
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/speakers", 
        json=speaker_data, 
        headers=token_headers
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == speaker_data["name"]
    assert response.json()["bio"] == speaker_data["bio"]

def test_get_speaker(client, test_speaker, token_headers):
    """Test para obtener un ponente específico"""
    response = client.get(
        f"{settings.API_V1_STR}/speakers/{test_speaker.id}", 
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == test_speaker.id
    assert response.json()["name"] == test_speaker.name

def test_update_speaker(client, test_speaker, token_headers):
    """Test para actualizar un ponente"""
    update_data = {
        "name": "Updated Speaker Name",
        "bio": "This is an updated test speaker bio with sufficient length to pass validation"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/speakers/{test_speaker.id}", 
        json=update_data, 
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["bio"] == update_data["bio"]