import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.session_service import SessionService
from app.models.event_attendee import EventAttendee
from app.models.session_attendee import SessionAttendee

class TestSessionServiceExtended:
    
    def test_unregister_from_session(self, db_session, test_session, test_user):
        """Test para darse de baja de una sesión"""
        session_service = SessionService(db=db_session)
        
        # Registrar al usuario en el evento
        event_attendee = EventAttendee(
            event_id=test_session.event_id,
            user_id=test_user.id
        )
        db_session.add(event_attendee)
        
        # Registrar al usuario en la sesión
        session_attendee = SessionAttendee(
            session_id=test_session.id,
            user_id=test_user.id
        )
        db_session.add(session_attendee)
        
        # Incrementar el contador de asistentes
        test_session.registered_attendees += 1
        db_session.add(test_session)
        db_session.commit()
        
        # Darse de baja de la sesión
        result = session_service.unregister_from_session(
            session_id=test_session.id,
            user_id=test_user.id
        )
        
        assert result is True
        
        # Verificar que ya no está registrado
        is_registered = session_service.is_user_registered(
            session_id=test_session.id,
            user_id=test_user.id
        )
        assert is_registered is False
        
        # Verificar que el contador disminuyó
        updated_session = session_service.get_session(session_id=test_session.id)
        assert updated_session.registered_attendees == 0
    
    def test_get_user_sessions(self, db_session, test_session, test_user):
        """Test para obtener sesiones registradas por un usuario"""
        session_service = SessionService(db=db_session)
        
        # Registrar al usuario en el evento
        event_attendee = EventAttendee(
            event_id=test_session.event_id,
            user_id=test_user.id
        )
        db_session.add(event_attendee)
        
        # Registrar al usuario en la sesión
        session_attendee = SessionAttendee(
            session_id=test_session.id,
            user_id=test_user.id
        )
        db_session.add(session_attendee)
        db_session.commit()
        
        # Obtener sesiones del usuario
        sessions = session_service.get_user_sessions(user_id=test_user.id)
        
        assert sessions is not None
        assert len(sessions) > 0
        assert sessions[0].id == test_session.id
    
    def test_delete_session(self, db_session, test_session, test_organizer):
        """Test para eliminar una sesión"""
        session_service = SessionService(db=db_session)
        
        result = session_service.delete_session(
            session_id=test_session.id,
            user_id=test_organizer.id
        )
        
        assert result is True
        
        # Verificar que la sesión fue eliminada
        deleted_session = session_service.get_session(session_id=test_session.id)
        assert deleted_session is None