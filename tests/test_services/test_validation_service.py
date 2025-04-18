import pytest
from datetime import datetime, timedelta
from app.services.validation_service import ValidationService
from app.models.event import EventStatus
from app.models.session import Session as EventSession
from app.models.user import UserRole

class TestValidationServiceExtended:
    
    def test_validate_session_create_full(self, db_session, test_event, test_organizer, test_speaker):
        """Test completo para validar creación de sesión"""
        validation_service = ValidationService(db=db_session)
        
        session_data = {
            "event_id": test_event.id,
            "title": "Test Session Complete",
            "description": "This is a complete test session with all required fields for validation",
            "speaker_id": test_speaker.id,
            "start_time": test_event.date + timedelta(hours=1),
            "end_time": test_event.date + timedelta(hours=3),
            "location": "Test Room",
            "capacity": 50
        }
        
        is_valid, error_msg = validation_service.validate_session_create(
            session_data=session_data,
            user=test_organizer
        )
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_validate_session_create_conflict(self, db_session, test_event, test_organizer, test_speaker, test_session):
        """Test para validar conflicto de horarios en sesiones"""
        validation_service = ValidationService(db=db_session)
        
        session_data = {
            "event_id": test_event.id,
            "title": "Conflicting Session",
            "description": "This session conflicts with an existing one in the same time slot",
            "speaker_id": test_speaker.id,
            "start_time": test_session.start_time,  # Mismo horario que test_session
            "end_time": test_session.end_time,
            "location": "Another Room",
            "capacity": 50
        }
        
        is_valid, error_msg = validation_service.validate_session_create(
            session_data=session_data,
            user=test_organizer
        )
        
        assert is_valid is False
        assert "conflicto" in error_msg.lower()
    
    def test_validate_session_update_capacity(self, db_session, test_session, test_organizer):
        """Test para validar actualización de capacidad de sesión"""
        validation_service = ValidationService(db=db_session)
        
        # Simulamos que hay personas registradas
        test_session.registered_attendees = 10
        db_session.add(test_session)
        db_session.commit()
        
        # Intentamos actualizar a una capacidad menor que los registrados
        update_data = {
            "capacity": 5
        }
        
        is_valid, error_msg = validation_service.validate_session_update(
            session_id=test_session.id,
            update_data=update_data,
            user=test_organizer
        )
        
        assert is_valid is False
        assert "capacidad" in error_msg.lower()
        assert "menor" in error_msg.lower()