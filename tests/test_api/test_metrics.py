# tests/test_api/test_metrics.py
import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_get_events_metrics(client, token_headers):
    """Test para obtener métricas de eventos"""
    response = client.get(f"{settings.API_V1_STR}/metrics/events", headers=token_headers)
    
    assert response.status_code == 200
    assert "total_events" in response.json()
    assert "events_by_status" in response.json()

def test_get_event_metrics(client, test_event, token_headers):
    """Test para obtener métricas de un evento específico"""
    response = client.get(
        f"{settings.API_V1_STR}/metrics/events/{test_event.id}", 
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert "basic_info" in response.json()
    assert response.json()["basic_info"]["id"] == test_event.id

def test_get_user_attendance_metrics(client, test_user, test_event, token_headers):
    """Test para obtener métricas de asistencia de un usuario"""
    # Primero registramos al usuario en un evento
    client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/register", 
        headers=token_headers
    )
    
    response = client.get(
        f"{settings.API_V1_STR}/metrics/users/me/attendance", 
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert "basic_info" in response.json()
    assert "attended_events" in response.json()