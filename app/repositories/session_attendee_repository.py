from typing import List, Optional, Set
from sqlalchemy.orm import Session

from app.models.session_attendee import SessionAttendee
from app.repositories.base import BaseRepository

class SessionAttendeeRepository:
    """
    Repository for SessionAttendee model
    """
    def register_user_to_session(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        session_id: int
    ) -> bool:
        """
        Register a user to a session
        """
        existing = (
            db.query(SessionAttendee)
            .filter(
                SessionAttendee.user_id == user_id,
                SessionAttendee.session_id == session_id
            )
            .first()
        )
        
        if existing:
            return True
        
        session_attendee = SessionAttendee(
            user_id=user_id,
            session_id=session_id
        )
        
        db.add(session_attendee)
        db.commit()
        return True
    
    def unregister_user_from_session(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        session_id: int
    ) -> bool:
        """
        Unregister a user from a session
        """
        existing = (
            db.query(SessionAttendee)
            .filter(
                SessionAttendee.user_id == user_id,
                SessionAttendee.session_id == session_id
            )
            .first()
        )
        
        if not existing:
            return False  
        
        db.delete(existing)
        db.commit()
        return True
    
    def is_user_registered_to_session(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        session_id: int
    ) -> bool:
        """
        Check if a user is registered to a session
        """
        return (
            db.query(SessionAttendee)
            .filter(
                SessionAttendee.user_id == user_id,
                SessionAttendee.session_id == session_id
            )
            .first()
        ) is not None
    
    def get_user_sessions(
        self, 
        db: Session, 
        *, 
        user_id: int
    ) -> List[int]:
        """
        Get all session IDs a user is registered to
        """
        registrations = (
            db.query(SessionAttendee)
            .filter(SessionAttendee.user_id == user_id)
            .all()
        )
        
        return [reg.session_id for reg in registrations]
    
    def get_session_attendees(
        self, 
        db: Session, 
        *, 
        session_id: int
    ) -> List[int]:
        """
        Get all user IDs registered to a session
        """
        registrations = (
            db.query(SessionAttendee)
            .filter(SessionAttendee.session_id == session_id)
            .all()
        )
        
        return [reg.user_id for reg in registrations]


session_attendee_repository = SessionAttendeeRepository()