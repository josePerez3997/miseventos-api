import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.session_service import SessionService
from app.schemas.session import SessionCreate, SessionUpdate

class TestSessionService:
    
    def test_get_sessions_by_event(self, db_session, test_event, test_session):
        """Test para obtener sesiones de un evento"""
        session_service = SessionService(db=db_session)
        
        sessions = session_service.get_sessions_by_event(event_id=test_event.id)
        
        assert sessions is not None
        assert len(sessions) > 0
        assert sessions[0].id == test_session.id
        assert sessions[0].event_id == test_event.id
    
    def test_register_for_session(self, db_session, test_session, test_user):
        """Test para registrarse a una sesión"""
        session_service = SessionService(db=db_session)
        
        # Primero registramos al usuario en el evento
        from app.models.event_attendee import EventAttendee
        attendee = EventAttendee(
            event_id=test_session.event_id,
            user_id=test_user.id
        )
        db_session.add(attendee)
        db_session.commit()
        
        # Ahora intentamos registrarlo en la sesión
        result = session_service.register_for_session(
            session_id=test_session.id,
            user_id=test_user.id
        )
        
        assert result is True
        
        # Verificar que está registrado
        is_registered = session_service.is_user_registered(
            session_id=test_session.id,
            user_id=test_user.id
        )
        assert is_registered is True
        
        # Verificar que el contador aumentó
        updated_session = session_service.get_session(session_id=test_session.id)
        assert updated_session.registered_attendees == 1
    
    def test_register_for_session_full(self, db_session, test_session, test_user):
        """Test para registrarse a una sesión llena"""
        session_service = SessionService(db=db_session)
        
        # Registrar al usuario en el evento
        from app.models.event_attendee import EventAttendee
        attendee = EventAttendee(
            event_id=test_session.event_id,
            user_id=test_user.id
        )
        db_session.add(attendee)
        
        # Marcar la sesión como llena
        test_session.capacity = 10
        test_session.registered_attendees = 10
        db_session.add(test_session)
        db_session.commit()
        
        # Intentar registrar al usuario debe fallar
        with pytest.raises(HTTPException) as excinfo:
            session_service.register_for_session(
                session_id=test_session.id,
                user_id=test_user.id
            )
        
        assert excinfo.value.status_code == 400
        assert "capacidad" in str(excinfo.value.detail).lower()