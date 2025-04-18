import pytest
from datetime import datetime
from jose import jwt

from app.services.auth_service import AuthService
from app.core.config import settings
from app.core.security import verify_password
from app.schemas.auth import Register, Login
from app.models.user import UserRole

class TestAuthService:
    def test_register_new_user(self, db_session):
        """Test para registrar un nuevo usuario"""
        auth_service = AuthService(db=db_session)
        user_data = Register(
            email="test_service@example.com",
            password="testpassword",
            name="Test Service User",
            role=UserRole.ATTENDEE
        )
        
        user = auth_service.register_new_user(user_data)
        
        assert user is not None
        assert user.email == user_data.email
        assert user.name == user_data.name
        assert user.role == user_data.role
        assert verify_password("testpassword", user.password_hash)
    
    def test_register_duplicate_email(self, db_session, test_user):
        """Test para registrar un usuario con email duplicado"""
        auth_service = AuthService(db=db_session)
        user_data = Register(
            email=test_user.email,  # Email ya existente
            password="testpassword",
            name="Duplicate Email User",
            role=UserRole.ATTENDEE
        )
        
        with pytest.raises(ValueError):
            auth_service.register_new_user(user_data)
    
    def test_authenticate_user_success(self, db_session, test_user):
        """Test para autenticar un usuario exitosamente"""
        auth_service = AuthService(db=db_session)
        
        user = auth_service.authenticate_user(
            email=test_user.email,
            password="testpassword"
        )
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_authenticate_user_wrong_password(self, db_session, test_user):
        """Test para autenticar un usuario con contraseña incorrecta"""
        auth_service = AuthService(db=db_session)
        
        user = auth_service.authenticate_user(
            email=test_user.email,
            password="wrongpassword"
        )
        
        assert user is None
    
    def test_authenticate_user_nonexistent(self, db_session):
        """Test para autenticar un usuario que no existe"""
        auth_service = AuthService(db=db_session)
        
        user = auth_service.authenticate_user(
            email="nonexistent@example.com",
            password="password"
        )
        
        assert user is None
    
    def test_create_token_for_user(self, db_session, test_user):
        """Test para crear un token para un usuario"""
        auth_service = AuthService(db=db_session)
        
        token_data = auth_service.create_token_for_user(test_user)
        
        assert token_data is not None
        assert token_data.token_type == "bearer"
        assert token_data.access_token is not None
        
        # Verificar que el token es válido y contiene el ID del usuario
        payload = jwt.decode(
            token_data.access_token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        
        assert int(payload["sub"]) == test_user.id
        assert "exp" in payload