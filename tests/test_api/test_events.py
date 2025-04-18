import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models.event import EventStatus

def test_get_events(client, token_headers):
    """Test para obtener eventos"""
    # Incluir token de autenticación si es necesario
    response = client.get(f"{settings.API_V1_STR}/events", headers=token_headers)
    
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "size" in response.json()
    assert "pages" in response.json()

def test_get_event(client, test_event, token_headers):
    """Test para obtener un evento específico"""
    # Incluir token de autenticación si es necesario
    response = client.get(f"{settings.API_V1_STR}/events/{test_event.id}", headers=token_headers)
    
    assert response.status_code == 200
    assert response.json()["id"] == test_event.id
    assert response.json()["name"] == test_event.name
    assert "organizer" in response.json()

def test_get_nonexistent_event(client, token_headers):
    """Test para obtener un evento que no existe"""
    # Incluir token de autenticación si es necesario
    response = client.get(f"{settings.API_V1_STR}/events/999999", headers=token_headers)
    
    assert response.status_code == 404
    assert "detail" in response.json()

def test_create_event_organizer(client, organizer_token_headers):
    """Test para crear un evento como organizador"""
    event_data = {
        "name": "New Test Event",
        "description": "This is a new test event created for testing with a long description that meets validation requirements",
        "location": "Test Location",
        "date": (datetime.now() + timedelta(days=10)).isoformat(),
        "capacity": 200,
        "status": EventStatus.UPCOMING
    }
    response = client.post(
        f"{settings.API_V1_STR}/events", 
        json=event_data, 
        headers=organizer_token_headers
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == event_data["name"]
    assert response.json()["description"] == event_data["description"]
    assert response.json()["location"] == event_data["location"]
    assert response.json()["capacity"] == event_data["capacity"]
    assert "id" in response.json()

def test_create_event_regular_user(client, token_headers):
    """Test para crear un evento como usuario regular (debe fallar)"""
    event_data = {
        "name": "Fail Event",
        "description": "This event should not be created because a regular user is attempting to create it",
        "location": "Test Location",
        "date": (datetime.now() + timedelta(days=10)).isoformat(),
        "capacity": 200,
        "status": EventStatus.UPCOMING
    }
    response = client.post(
        f"{settings.API_V1_STR}/events", 
        json=event_data, 
        headers=token_headers
    )
    
    # El código de estado puede ser 400 o 403 dependiendo de la implementación
    assert response.status_code in [400, 403]
    assert "detail" in response.json()

def test_create_event_past_date(client, organizer_token_headers):
    """Test para crear un evento con fecha pasada (debe fallar)"""
    event_data = {
        "name": "Past Event",
        "description": "This event has a past date and should be rejected by the validation system",
        "location": "Test Location",
        "date": (datetime.now() - timedelta(days=10)).isoformat(),
        "capacity": 200,
        "status": EventStatus.UPCOMING
    }
    response = client.post(
        f"{settings.API_V1_STR}/events", 
        json=event_data, 
        headers=organizer_token_headers
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()

def test_update_event_organizer(client, organizer_token_headers, test_event):
    """Test para actualizar un evento como organizador"""
    update_data = {
        "name": "Updated Event Name",
        "description": "This is an updated description with sufficient length to pass validation"
    }
    response = client.put(
        f"{settings.API_V1_STR}/events/{test_event.id}", 
        json=update_data, 
        headers=organizer_token_headers
    )
    
    # En caso de que el test falle, obtener más información
    if response.status_code != 200:
        print(f"Error updating event: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["description"] == update_data["description"]
    assert response.json()["id"] == test_event.id

def test_update_event_other_user(client, token_headers, test_event):
    """Test para actualizar un evento como otro usuario (debe fallar)"""
    update_data = {
        "name": "Fail Update",
        "description": "This update should fail because a non-organizer user is attempting it"
    }
    response = client.put(
        f"{settings.API_V1_STR}/events/{test_event.id}", 
        json=update_data, 
        headers=token_headers
    )
    
    # El código puede ser 400, 403 o 404 dependiendo de la implementación
    assert response.status_code in [400, 403, 404]
    assert "detail" in response.json()

def test_update_event_invalid_capacity(client, organizer_token_headers, test_event):
    """Test para actualizar un evento con capacidad inválida (debe fallar)"""
    update_data = {
        "capacity": -10,
        "description": "This update should fail due to invalid capacity but the description is valid"
    }
    response = client.put(
        f"{settings.API_V1_STR}/events/{test_event.id}", 
        json=update_data, 
        headers=organizer_token_headers
    )
    
    # El código debe ser 400 o 422 dependiendo de la validación
    assert response.status_code in [400, 422]
    
    # Podría tener "detail" o "validation_error" dependiendo de la implementación
    assert response.json().get("detail") is not None or "validation_error" in response.json()

def test_delete_event_organizer(client, organizer_token_headers, test_event):
    """Test para eliminar un evento como organizador"""
    response = client.delete(
        f"{settings.API_V1_STR}/events/{test_event.id}", 
        headers=organizer_token_headers
    )
    
    # El código debe ser 204 o 200 dependiendo de la implementación
    assert response.status_code in [204, 200]
    
    # Verificar que el evento ya no existe
    get_response = client.get(
        f"{settings.API_V1_STR}/events/{test_event.id}", 
        headers=organizer_token_headers
    )
    assert get_response.status_code == 404

def test_delete_event_other_user(client, token_headers, test_event):
    """Test para eliminar un evento como otro usuario (debe fallar)"""
    response = client.delete(
        f"{settings.API_V1_STR}/events/{test_event.id}", 
        headers=token_headers
    )
    
    # El código puede ser 400, 403 o 404 dependiendo de la implementación
    assert response.status_code in [400, 403, 404]
    assert "detail" in response.json()

def test_register_for_event(client, token_headers, test_event):
    """Test para registrarse a un evento"""
    response = client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/register", 
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Verificar que el usuario está registrado
    response = client.get(
        f"{settings.API_V1_STR}/events/{test_event.id}/registration-status", 
        headers=token_headers
    )
    assert response.status_code == 200
    assert response.json()["is_registered"] == True

def test_register_for_event_already_registered(client, token_headers, test_event):
    """Test para registrarse a un evento ya registrado"""
    # Primero registramos al usuario
    client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/register", 
        headers=token_headers
    )
    
    # Intentamos registrarlo de nuevo
    response = client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/register", 
        headers=token_headers
    )
    
    # Si ya está registrado, la implementación puede devolver 200 (éxito) o 400 (error)
    # dependiendo de si se considera un error intentar registrar de nuevo
    assert response.status_code in [200, 400]
    
    # En cualquier caso, el usuario debe seguir registrado
    response = client.get(
        f"{settings.API_V1_STR}/events/{test_event.id}/registration-status", 
        headers=token_headers
    )
    assert response.status_code == 200
    assert response.json()["is_registered"] == True

def test_unregister_from_event(client, token_headers, test_event):
    """Test para darse de baja de un evento"""
    # Primero registramos al usuario
    client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/register", 
        headers=token_headers
    )
    
    # Ahora lo damos de baja
    response = client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/unregister", 
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Verificar que el usuario ya no está registrado
    response = client.get(
        f"{settings.API_V1_STR}/events/{test_event.id}/registration-status", 
        headers=token_headers
    )
    assert response.status_code == 200
    assert response.json()["is_registered"] == False

def test_unregister_from_event_not_registered(client, token_headers, test_event):
    """Test para darse de baja de un evento al que no está registrado (debe fallar)"""
    response = client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/unregister", 
        headers=token_headers
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()

def test_get_registered_events(client, token_headers, test_event):
    """Test para obtener eventos registrados"""
    # Primero registramos al usuario en un evento
    client.post(
        f"{settings.API_V1_STR}/events/{test_event.id}/register", 
        headers=token_headers
    )
    
    response = client.get(
        f"{settings.API_V1_STR}/events/registered", 
        headers=token_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == test_event.id

def test_get_my_events_organizer(client, organizer_token_headers, test_event):
    """Test para obtener eventos organizados por el usuario"""
    response = client.get(
        f"{settings.API_V1_STR}/events/my", 
        headers=organizer_token_headers
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == test_event.id