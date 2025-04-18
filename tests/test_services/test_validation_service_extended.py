import pytest
from datetime import datetime, timedelta
from app.services.validation_service import ValidationService
from app.models.user import UserRole
from app.models.event import EventStatus

class TestValidationServiceExtended:
    
    def test_validate_session_update_nonexistent(self, db_session, test_organizer):
        """Test para validar actualización de sesión inexistente"""
        validation_service = ValidationService(db=db_session)
        
        update_data = {
            "title": "Updated Session Title"
        }
        
        is_valid, error_msg = validation_service.validate_session_update(
            session_id=99999,  # ID que no existe
            update_data=update_data,
            user=test_organizer
        )
        
        assert is_valid is False
        assert "no encontrada" in error_msg.lower()
    
    def test_validate_session_update_other_user(self, db_session, test_session, test_user):
        """Test para validar actualización de sesión por otro usuario"""
        validation_service = ValidationService(db=db_session)
        
        update_data = {
            "title": "Unauthorized Update"
        }
        
        is_valid, error_msg = validation_service.validate_session_update(
            session_id=test_session.id,
            update_data=update_data,
            user=test_user  # No es el organizador
        )
        
        assert is_valid is False
        assert "permiso" in error_msg.lower()
    
    def test_validate_event_update_completed(self, db_session, test_event, test_organizer):
        """Test para validar actualización de evento completado"""
        validation_service = ValidationService(db=db_session)
        
        # Marcar el evento como completado
        test_event.status = EventStatus.COMPLETED
        db_session.add(test_event)
        db_session.commit()
        
        update_data = {
            "name": "Updated Event Name"
        }
        
        is_valid, error_msg = validation_service.validate_event_update(
            event_id=test_event.id,
            update_data=update_data,
            user=test_organizer
        )
        
        assert is_valid is False
        assert "estado" in error_msg.lower()
        
        # Restaurar estado original
        test_event.status = EventStatus.UPCOMING
        db_session.add(test_event)
        db_session.commit()