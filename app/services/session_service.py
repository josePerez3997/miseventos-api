from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.db import get_database
from app.repositories.session_repository import session_repository
from app.repositories.session_attendee_repository import session_attendee_repository
from app.repositories.event_repository import event_repository
from app.repositories.user_repository import user_repository
from app.models.session import Session as EventSession
from app.schemas.session import SessionCreate, SessionUpdate
from app.services.validation_service import ValidationService

class SessionService:
    """
    Service for session related operations
    """
    def __init__(
        self, 
        db: SQLAlchemySession = Depends(get_database),
        validation_service: ValidationService = Depends()
    ):
        self.db = db
        self.validation_service = validation_service
    
    def get_session(self, session_id: int) -> Optional[EventSession]:
        """
        Get a session by ID
        """
        return session_repository.get(self.db, id=session_id)
    
    def get_sessions_by_event(self, event_id: int) -> List[EventSession]:
        """
        Get all sessions for an event
        """
        return session_repository.get_by_event(self.db, event_id=event_id)
    
    def create_session(self, session_in: SessionCreate, user_id: int) -> Optional[EventSession]:
        """
        Create a new session for an event with validations
        
        Raises:
        - HTTPException: If validation fails
        """
        session_data = session_in.model_dump()
        
        user = user_repository.get(self.db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        is_valid, error_msg = self.validation_service.validate_session_create(
            session_data, user
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        return session_repository.create(self.db, obj_in=session_data)
    
    def update_session(
        self, 
        session_id: int, 
        session_in: SessionUpdate, 
        user_id: int
    ) -> Optional[EventSession]:
        """
        Update a session with validations
        
        Raises:
        - HTTPException: If validation fails
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        update_data = session_in.model_dump(exclude_unset=True)
        
        user = user_repository.get(self.db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        is_valid, error_msg = self.validation_service.validate_session_update(
            session_id, update_data, user
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        return session_repository.update(self.db, db_obj=session, obj_in=update_data)
    
    def delete_session(self, session_id: int, user_id: int) -> bool:
        """
        Delete a session (only by event organizer)
        
        Raises:
        - HTTPException: If validation fails
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        event = event_repository.get(self.db, id=session.event_id)
        user = user_repository.get(self.db, id=user_id)
        
        if not event or not user:
            return False
        
        if event.organizer_id != user_id and user.role != "ADMIN":
            return False
        
        if event.status not in ["UPCOMING", "ONGOING"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pueden eliminar sesiones de eventos con estado {event.status}"
            )
        
        if session.registered_attendees > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una sesión con asistentes registrados"
            )
        
        session_repository.remove(self.db, id=session_id)
        return True
    
    def register_for_session(self, session_id: int, user_id: int) -> bool:
        """
        Register a user for a session
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        if session.registered_attendees >= session.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La sesión ha alcanzado su capacidad máxima"
            )
        
        event = event_repository.get(self.db, id=session.event_id)
        if not event:
            return False
        
        is_registered_to_event = any(
            attendee.user_id == user_id for attendee in event.attendees
        )
        
        if not is_registered_to_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debes estar registrado en el evento para asistir a esta sesión"
            )
        
        is_registered = session_attendee_repository.is_user_registered_to_session(
            self.db, user_id=user_id, session_id=session_id
        )
        
        if is_registered:
            return True
        
        user_sessions = self.get_user_sessions(user_id=user_id)
        for user_session in user_sessions:
            if (session.start_time < user_session.end_time and 
                session.end_time > user_session.start_time):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tienes un conflicto de horario con la sesión: {user_session.title}"
                )
        
        registration_success = session_attendee_repository.register_user_to_session(
            self.db, user_id=user_id, session_id=session_id
        )
        
        if registration_success:
            session_repository.register_attendee(self.db, session_id=session_id)
            return True
        
        return False
    
    def unregister_from_session(self, session_id: int, user_id: int) -> bool:
        """
        Unregister a user from a session
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        event = event_repository.get(self.db, id=session.event_id)
        if not event:
            return False
        
        current_time = datetime.now()
        if session.start_time < current_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes cancelar asistencia a una sesión que ya ha comenzado"
            )
        
        time_before_start = (session.start_time - current_time).total_seconds() / 3600  
        if time_before_start < 2: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes cancelar asistencia a menos de 2 horas del inicio de la sesión"
            )
        
        is_registered = session_attendee_repository.is_user_registered_to_session(
            self.db, user_id=user_id, session_id=session_id
        )
        
        if not is_registered:
            return False
        
        unregistration_success = session_attendee_repository.unregister_user_from_session(
            self.db, user_id=user_id, session_id=session_id
        )
        
        if unregistration_success:
            session_repository.unregister_attendee(self.db, session_id=session_id)
            return True
        
        return False
    
    def is_user_registered(self, session_id: int, user_id: int) -> bool:
        """
        Check if a user is registered for a session
        """
        return session_attendee_repository.is_user_registered_to_session(
            self.db, user_id=user_id, session_id=session_id
        )
    
    def get_user_sessions(self, user_id: int) -> List[EventSession]:
        """
        Get all sessions a user is registered for
        """
        session_ids = session_attendee_repository.get_user_sessions(
            self.db, user_id=user_id
        )
        
        if not session_ids:
            return []
        
        sessions = []
        for session_id in session_ids:
            session = self.get_session(session_id)
            if session:
                sessions.append(session)
        
        return sessions