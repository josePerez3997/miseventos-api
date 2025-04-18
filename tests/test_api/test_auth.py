import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.user import UserRole

def test_login(client, test_user):
    """Test para el inicio de sesión"""
    login_data = {
        "username": test_user.email,
        "password": "testpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_incorrect_password(client, test_user):
    """Test para el inicio de sesión con contraseña incorrecta"""
    login_data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    
    assert response.status_code == 401
    assert "detail" in response.json()

def test_login_nonexistent_user(client):
    """Test para el inicio de sesión con usuario inexistente"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    
    assert response.status_code == 401
    assert "detail" in response.json()

def test_register(client):
    """Test para el registro de usuario"""
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "name": "New User",
        "role": UserRole.ATTENDEE
    }
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
    
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
    assert response.json()["name"] == user_data["name"]
    assert response.json()["role"] == user_data["role"]
    assert "id" in response.json()

def test_register_duplicate_email(client, test_user):
    """Test para el registro con email duplicado"""
    user_data = {
        "email": test_user.email,  # Email ya existente
        "password": "newpassword",
        "name": "New User",
        "role": UserRole.ATTENDEE
    }
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
    
    assert response.status_code == 400
    assert "detail" in response.json()

def test_test_token(client, token_headers):
    """Test para verificar token de autenticación"""
    response = client.get(f"{settings.API_V1_STR}/auth/test-token", headers=token_headers)
    
    assert response.status_code == 200
    assert "email" in response.json()
    assert "id" in response.json()

def test_test_token_invalid(client):
    """Test para verificar token inválido"""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get(f"{settings.API_V1_STR}/auth/test-token", headers=headers)
    
    assert response.status_code == 401
    assert "detail" in response.json()