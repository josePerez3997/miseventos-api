import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.user import UserRole

def test_read_users_me(client, token_headers, test_user):
    """Test para obtener el usuario actual"""
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=token_headers)
    
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
    assert response.json()["name"] == test_user.name
    assert response.json()["id"] == test_user.id

def test_update_user_me(client, token_headers):
    """Test para actualizar el usuario actual"""
    update_data = {
        "name": "Updated Name"
    }
    response = client.put(f"{settings.API_V1_STR}/users/me", json=update_data, headers=token_headers)
    
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

def test_update_user_me_email(client, token_headers, test_user):
    """Test para actualizar el email del usuario actual"""
    update_data = {
        "email": "newemail@example.com"
    }
    response = client.put(f"{settings.API_V1_STR}/users/me", json=update_data, headers=token_headers)
    
    assert response.status_code == 200
    assert response.json()["email"] == update_data["email"]

def test_update_user_me_duplicate_email(client, token_headers, test_organizer):
    """Test para actualizar el email del usuario actual con uno ya existente"""
    update_data = {
        "email": test_organizer.email  # Email de otro usuario
    }
    response = client.put(f"{settings.API_V1_STR}/users/me", json=update_data, headers=token_headers)
    
    assert response.status_code == 400
    assert "detail" in response.json()

def test_read_users_normal_user(client, token_headers):
    """Test para obtener lista de usuarios como usuario normal (debe fallar)"""
    response = client.get(f"{settings.API_V1_STR}/users", headers=token_headers)
    
    assert response.status_code == 403
    assert "detail" in response.json()

def test_read_users_admin(client, admin_token_headers):
    """Test para obtener lista de usuarios como administrador"""
    response = client.get(f"{settings.API_V1_STR}/users", headers=admin_token_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_read_user_admin(client, admin_token_headers, test_user):
    """Test para obtener un usuario específico como administrador"""
    response = client.get(f"{settings.API_V1_STR}/users/{test_user.id}", headers=admin_token_headers)
    
    assert response.status_code == 200
    assert response.json()["id"] == test_user.id
    assert response.json()["email"] == test_user.email

def test_read_user_normal_user(client, token_headers, test_organizer):
    """Test para obtener un usuario específico como usuario normal (debe fallar)"""
    response = client.get(f"{settings.API_V1_STR}/users/{test_organizer.id}", headers=token_headers)
    
    assert response.status_code == 403
    assert "detail" in response.json()

def test_create_user_admin(client, admin_token_headers):
    """Test para crear un usuario como administrador"""
    user_data = {
        "email": "adminuser@example.com",
        "password": "adminuserpass",
        "name": "Admin Created User",
        "role": UserRole.ATTENDEE
    }
    response = client.post(f"{settings.API_V1_STR}/users", json=user_data, headers=admin_token_headers)
    
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
    assert response.json()["name"] == user_data["name"]
    assert response.json()["role"] == user_data["role"]

def test_create_user_normal_user(client, token_headers):
    """Test para crear un usuario como usuario normal (debe fallar)"""
    user_data = {
        "email": "failuser@example.com",
        "password": "password",
        "name": "Fail User",
        "role": UserRole.ATTENDEE
    }
    response = client.post(f"{settings.API_V1_STR}/users", json=user_data, headers=token_headers)
    
    assert response.status_code == 403
    assert "detail" in response.json()

def test_update_user_admin(client, admin_token_headers, test_user):
    """Test para actualizar un usuario como administrador"""
    update_data = {
        "name": "Admin Updated Name",
        "role": UserRole.ORGANIZER
    }
    response = client.put(f"{settings.API_V1_STR}/users/{test_user.id}", json=update_data, headers=admin_token_headers)
    
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["role"] == update_data["role"]

def test_update_user_normal_user(client, token_headers, test_organizer):
    """Test para actualizar un usuario como usuario normal (debe fallar)"""
    update_data = {
        "name": "Fail Update"
    }
    response = client.put(f"{settings.API_V1_STR}/users/{test_organizer.id}", json=update_data, headers=token_headers)
    
    assert response.status_code == 403
    assert "detail" in response.json()

def test_delete_user_admin(client, admin_token_headers, test_user):
    """Test para eliminar un usuario como administrador"""
    response = client.delete(f"{settings.API_V1_STR}/users/{test_user.id}", headers=admin_token_headers)
    
    assert response.status_code == 200
    assert response.json()["id"] == test_user.id
    
    # Verificar que el usuario ya no existe
    response = client.get(f"{settings.API_V1_STR}/users/{test_user.id}", headers=admin_token_headers)
    assert response.status_code == 404

def test_delete_user_normal_user(client, token_headers, test_organizer):
    """Test para eliminar un usuario como usuario normal (debe fallar)"""
    response = client.delete(f"{settings.API_V1_STR}/users/{test_organizer.id}", headers=token_headers)
    
    assert response.status_code == 403
    assert "detail" in response.json()