from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.db import get_database
from app.repositories.session_repository import session_repository
from app.repositories.session_attendee_repository import session_attendee_repository
from app.repositories.event_repository import event_repository
from app.models.session import Session as EventSession
from app.schemas.session import SessionCreate, SessionUpdate

class SessionService:
    """
    Service for session related operations
    """
    def __init__(self, db: SQLAlchemySession = Depends(get_database)):
        self.db = db
    
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
        Create a new session for an event (only by event organizer)
        """
        event = event_repository.get(self.db, id=session_in.event_id)
        if not event or event.organizer_id != user_id:
            return None
        
        has_conflict = session_repository.check_time_conflict(
            self.db, 
            event_id=session_in.event_id, 
            start_time=session_in.start_time, 
            end_time=session_in.end_time
        )
        
        if has_conflict:
            return None
        
        return session_repository.create(self.db, obj_in=session_in)
    
    def update_session(
        self, 
        session_id: int, 
        session_in: SessionUpdate, 
        user_id: int
    ) -> Optional[EventSession]:
        """
        Update a session (only by event organizer)
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        event = event_repository.get(self.db, id=session.event_id)
        if not event or event.organizer_id != user_id:
            return None
        
        if session_in.start_time or session_in.end_time:
            start_time = session_in.start_time or session.start_time
            end_time = session_in.end_time or session.end_time
            
            has_conflict = session_repository.check_time_conflict(
                self.db, 
                event_id=session.event_id, 
                start_time=start_time, 
                end_time=end_time,
                session_id=session_id
            )
            
            if has_conflict:
                return None
        
        return session_repository.update(self.db, db_obj=session, obj_in=session_in)
    
    def delete_session(self, session_id: int, user_id: int) -> bool:
        """
        Delete a session (only by event organizer)
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        event = event_repository.get(self.db, id=session.event_id)
        if not event or event.organizer_id != user_id:
            return False
        
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
            return False
        
        registration_success = session_attendee_repository.register_user_to_session(
            self.db, 
            user_id=user_id, 
            session_id=session_id
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
        
        if not session_attendee_repository.is_user_registered_to_session(
            self.db, 
            user_id=user_id, 
            session_id=session_id
        ):
            return False
        
        unregistration_success = session_attendee_repository.unregister_user_from_session(
            self.db, 
            user_id=user_id, 
            session_id=session_id
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
            self.db, 
            user_id=user_id, 
            session_id=session_id
        )
    
    def get_user_sessions(self, user_id: int) -> List[EventSession]:
        """
        Get all sessions a user is registered for
        """
        session_ids = session_attendee_repository.get_user_sessions(
            self.db, 
            user_id=user_id
        )
        
        if not session_ids:
            return []
        
        sessions = []
        for session_id in session_ids:
            session = self.get_session(session_id)
            if session:
                sessions.append(session)
        
        return sessions