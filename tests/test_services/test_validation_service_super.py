import pytest
from datetime import datetime, timedelta
from app.services.validation_service import ValidationService

class TestValidationServiceSuper:
    
    def test_validate_event_create_invalid_name(self, db_session, test_organizer):
        """Test para validar creación de evento con nombre inválido"""
        validation_service = ValidationService(db=db_session)
        
        event_data = {
            "name": "AB",  # Nombre demasiado corto
            "description": "This is a test event with a valid description",
            "location": "Test Location",
            "date": datetime.now() + timedelta(days=10),
            "capacity": 100
        }
        
        is_valid, error_msg = validation_service.validate_event_create(
            event_data=event_data,
            user=test_organizer
        )
        
        assert is_valid is False
        assert "nombre" in error_msg.lower()
    
    def test_validate_event_create_invalid_description(self, db_session, test_organizer):
        """Test para validar creación de evento con descripción inválida"""
        validation_service = ValidationService(db=db_session)
        
        event_data = {
            "name": "Valid Event Name",
            "description": "Too short",  # Descripción demasiado corta
            "location": "Test Location",
            "date": datetime.now() + timedelta(days=10),
            "capacity": 100
        }
        
        is_valid, error_msg = validation_service.validate_event_create(
            event_data=event_data,
            user=test_organizer
        )
        
        assert is_valid is False
        assert "descripción" in error_msg.lower()
    
    def test_validate_event_update_nonexistent(self, db_session, test_organizer):
        """Test para validar actualización de evento inexistente"""
        validation_service = ValidationService(db=db_session)
        
        update_data = {
            "name": "Updated Event Name"
        }
        
        is_valid, error_msg = validation_service.validate_event_update(
            event_id=99999,  # ID que no existe
            update_data=update_data,
            user=test_organizer
        )
        
        assert is_valid is False
        assert "no encontrado" in error_msg.lower()