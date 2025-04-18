import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.core.config import settings

def test_get_sessions_by_event(client, test_event, test_session, token_headers):
    """Test para obtener sesiones de un evento"""
    response = client.get(
        f"{settings.API_V1_STR}/sessions/event/{test_event.id}", 
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.skip(reason="SQLite DateTime conversion issues")
def test_create_session(client, organizer_token_headers, test_event, test_speaker):
    """Test para crear una sesión"""
    import json
    from datetime import datetime, timedelta
    
    # Obtener fecha base del evento
    event_date = test_event.date
    
    # Construir objetos datetime para las horas de inicio y fin
    # Eliminar microsegundos para evitar problemas con SQLite
    start_time = event_date.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = event_date.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # Convertir a strings ISO para JSON
    start_time_str = start_time.isoformat()
    end_time_str = end_time.isoformat()
    
    session_data = {
        "event_id": test_event.id,
        "title": "API Test Session",
        "description": "This is a session created via API test with a sufficiently long description",
        "speaker_id": test_speaker.id,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "location": "API Test Room",
        "capacity": 40
    }
    
    # Asegurarnos que las fechas están en el formato correcto
    print(f"Start time: {session_data['start_time']}")
    print(f"End time: {session_data['end_time']}")
    
    response = client.post(
        f"{settings.API_V1_STR}/sessions", 
        json=session_data,
        headers=organizer_token_headers
    )
    
    # Si hay error, imprimirlo para depuración
    if response.status_code != 201:
        print(f"Error response: {response.json()}")
    
    assert response.status_code == 201

def test_get_session(client, test_session, token_headers):
    """Test para obtener una sesión específica"""
    response = client.get(
        f"{settings.API_V1_STR}/sessions/{test_session.id}", 
        headers=token_headers
    )
    
    assert response.status_code == 200