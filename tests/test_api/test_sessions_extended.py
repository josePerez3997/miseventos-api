import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_update_session(client, test_session, organizer_token_headers):
    """Test para actualizar una sesión"""
    update_data = {
        "title": "Updated Session Title",
        "description": "This is an updated session description that is sufficiently long for validation"
    }
    
    response = client.put(
        f"{settings.API_V1_STR}/sessions/{test_session.id}",
        json=update_data,
        headers=organizer_token_headers
    )
    
    assert response.status_code == 200

def test_delete_session(client, test_session, organizer_token_headers):
    """Test para eliminar una sesión"""
    response = client.delete(
        f"{settings.API_V1_STR}/sessions/{test_session.id}",
        headers=organizer_token_headers
    )
    
    assert response.status_code == 204
    
    # Verificar que ya no existe
    get_response = client.get(
        f"{settings.API_V1_STR}/sessions/{test_session.id}",
        headers=organizer_token_headers
    )
    assert get_response.status_code == 404

def test_register_for_session(client, test_session, test_event, token_headers):
    """Test para registrarse a una sesión"""
    # Primero registramos al usuario en el evento
    client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/register",
        headers=token_headers
    )
    
    response = client.post(
        f"{settings.API_V1_STR}/sessions/{test_session.id}/register",
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verificar el estado de registro
    status_response = client.get(
        f"{settings.API_V1_STR}/sessions/{test_session.id}/registration-status",
        headers=token_headers
    )
    assert status_response.status_code == 200
    assert status_response.json()["is_registered"] is True