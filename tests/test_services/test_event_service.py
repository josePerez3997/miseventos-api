import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.services.event_service import EventService
from app.services.validation_service import ValidationService
from app.schemas.event import EventCreate, EventUpdate, EventSearchParams
from app.models.event import EventStatus
from app.models.event_attendee import EventAttendee

class TestEventService:
    def test_get_event(self, db_session, test_event):
        """Test para obtener un evento por ID"""
        event_service = EventService(db=db_session)
        
        event = event_service.get_event(event_id=test_event.id)
        
        assert event is not None
        assert event.id == test_event.id
        assert event.name == test_event.name
        assert event.description == test_event.description
    
    def test_get_event_nonexistent(self, db_session):
        """Test para obtener un evento que no existe"""
        event_service = EventService(db=db_session)
        
        event = event_service.get_event(event_id=999999)
        
        assert event is None
    
    def test_get_events(self, db_session, test_event):
        """Test para obtener eventos con filtros"""
        event_service = EventService(db=db_session)
        
        params = EventSearchParams(
            search=None,
            status=None,
            page=1,
            size=10
        )
        
        result = event_service.get_events(params=params)
        
        assert result is not None
        assert "items" in result
        assert "total" in result
        assert "page" in result
        assert "size" in result
        assert "pages" in result
        assert len(result["items"]) > 0
    
    def test_get_events_with_search(self, db_session, test_event):
        """Test para obtener eventos con búsqueda"""
        event_service = EventService(db=db_session)
        
        # Búsqueda que debe encontrar el evento de prueba
        params = EventSearchParams(
            search="Test",
            status=None,
            page=1,
            size=10
        )
        
        result = event_service.get_events(params=params)
        
        assert result is not None
        assert len(result["items"]) > 0
        assert any(event.id == test_event.id for event in result["items"])
        
        # Búsqueda que no debe encontrar nada
        params = EventSearchParams(
            search="NonexistentEvent",
            status=None,
            page=1,
            size=10
        )
        
        result = event_service.get_events(params=params)
        
        assert result is not None
        assert len(result["items"]) == 0
    
    def test_get_events_by_organizer(self, db_session, test_event, test_organizer):
        """Test para obtener eventos por organizador"""
        event_service = EventService(db=db_session)
        
        events = event_service.get_events_by_organizer(organizer_id=test_organizer.id)
        
        assert events is not None
        assert len(events) > 0
        assert events[0].id == test_event.id
        assert events[0].organizer_id == test_organizer.id
    
    def test_create_event(self, db_session, test_organizer):
        """Test para crear un evento"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        event_data = EventCreate(
            name="Service Test Event",
            description="This is a test event created by the service test with a sufficiently long description",
            location="Service Test Location",
            date=datetime.now() + timedelta(days=10),
            capacity=150,
            status=EventStatus.UPCOMING
        )
        
        event = event_service.create_event(
            event_in=event_data,
            organizer_id=test_organizer.id
        )
        
        assert event is not None
        assert event.name == event_data.name
        assert event.description == event_data.description
        assert event.location == event_data.location
        assert event.capacity == event_data.capacity
        assert event.status == event_data.status
        assert event.organizer_id == test_organizer.id
        assert event.registered_attendees == 0
    
    def test_create_event_past_date(self, db_session, test_organizer):
        """Test para crear un evento con fecha pasada (debe fallar)"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        event_data = EventCreate(
            name="Past Date Event",
            description="This event has a past date but has a sufficiently long description for validation",
            location="Test Location",
            date=datetime.now() - timedelta(days=10),
            capacity=150,
            status=EventStatus.UPCOMING
        )
        
        with pytest.raises(HTTPException) as excinfo:
            event_service.create_event(
                event_in=event_data,
                organizer_id=test_organizer.id
            )
        
        assert excinfo.value.status_code == 400
    
    def test_update_event(self, db_session, test_event, test_organizer):
        """Test para actualizar un evento"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        # Usa un dict en lugar de EventUpdate para evitar problemas de validación
        update_data = {
            "name": "Updated Service Test Event",
            "description": "This is an updated description with sufficient length to pass validation"
        }
        
        # Adaptamos el método para usar un dict
        event = event_service.update_event(
            event_id=test_event.id,
            event_in=update_data,
            user_id=test_organizer.id
        )
        
        assert event is not None
        assert event.id == test_event.id
        assert event.name == update_data["name"]
        assert event.description == update_data["description"]
    
    def test_update_event_other_user(self, db_session, test_event, test_user):
        """Test para actualizar un evento como otro usuario (debe fallar)"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        # Usa un dict en lugar de EventUpdate
        update_data = {
            "name": "Fail Update",
            "description": "This update should fail because it's from another user, but the description is valid"
        }
        
        with pytest.raises(HTTPException) as excinfo:
            event_service.update_event(
                event_id=test_event.id,
                event_in=update_data,
                user_id=test_user.id
            )
        
        assert excinfo.value.status_code in [400, 403, 404]
    
    def test_delete_event(self, db_session, test_event, test_organizer):
        """Test para eliminar un evento"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        result = event_service.delete_event(
            event_id=test_event.id,
            user_id=test_organizer.id
        )
        
        assert result is True
        
        # Verificar que el evento ya no existe
        event = event_service.get_event(event_id=test_event.id)
        assert event is None
    
    def test_delete_event_other_user(self, db_session, test_event, test_user):
        """Test para eliminar un evento como otro usuario (debe fallar)"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        result = event_service.delete_event(
            event_id=test_event.id,
            user_id=test_user.id
        )
        
        assert result is False
    
    def test_register_for_event(self, db_session, test_event, test_user):
        """Test para registrarse a un evento"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        result = event_service.register_for_event(
            event_id=test_event.id,
            user_id=test_user.id
        )
        
        assert result is True
        
        # Verificar que el usuario está registrado
        is_registered = event_service.is_user_registered(
            event_id=test_event.id,
            user_id=test_user.id
        )
        assert is_registered is True
        
        # Verificar que el contador de asistentes aumentó
        event = event_service.get_event(event_id=test_event.id)
        assert event.registered_attendees == 1
    
    def test_unregister_from_event(self, db_session, test_event, test_user):
        """Test para darse de baja de un evento"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        # Primero registramos al usuario
        event_service.register_for_event(
            event_id=test_event.id,
            user_id=test_user.id
        )
        
        # Ahora lo damos de baja
        result = event_service.unregister_from_event(
            event_id=test_event.id,
            user_id=test_user.id
        )
        
        assert result is True
        
        # Verificar que el usuario ya no está registrado
        is_registered = event_service.is_user_registered(
            event_id=test_event.id,
            user_id=test_user.id
        )
        assert is_registered is False
        
        # Verificar que el contador de asistentes disminuyó
        event = event_service.get_event(event_id=test_event.id)
        assert event.registered_attendees == 0
    
    def test_get_user_registered_events(self, db_session, test_event, test_user):
        """Test para obtener eventos registrados por un usuario"""
        validation_service = ValidationService(db=db_session)
        event_service = EventService(
            db=db_session,
            validation_service=validation_service
        )
        
        # Primero registramos al usuario en un evento
        event_service.register_for_event(
            event_id=test_event.id,
            user_id=test_user.id
        )
        
        events = event_service.get_user_registered_events(
            user_id=test_user.id
        )
        
        assert events is not None
        assert len(events) > 0
        assert events[0].id == test_event.id