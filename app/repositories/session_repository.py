from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate
from app.repositories.base import BaseRepository

class SessionRepository(BaseRepository[Session, SessionCreate, SessionUpdate]):
    """
    Repository for Session model
    """
    def get_by_event(self, db: Session, *, event_id: int) -> List[Session]:
        """
        Get sessions by event
        """
        return db.query(Session).filter(Session.event_id == event_id).all()
    
    def get_by_speaker(self, db: Session, *, speaker_id: int) -> List[Session]:
        """
        Get sessions by speaker
        """
        return db.query(Session).filter(Session.speaker_id == speaker_id).all()
    
    def check_time_conflict(
        self, 
        db: Session, 
        *, 
        event_id: int, 
        start_time: datetime, 
        end_time: datetime,
        session_id: Optional[int] = None
    ) -> bool:
        """
        Check if there's a session time conflict
        Returns True if there is a conflict, False otherwise
        """
        query = db.query(Session).filter(
            and_(
                Session.event_id == event_id,
                or_(
                    and_(
                        Session.start_time <= start_time,
                        Session.end_time > start_time
                    ),
                    and_(
                        Session.start_time < end_time,
                        Session.end_time >= end_time
                    ),
                    and_(
                        Session.start_time >= start_time,
                        Session.end_time <= end_time
                    )
                )
            )
        )
        
        if session_id:
            query = query.filter(Session.id != session_id)
        
        return db.query(query.exists()).scalar()
    
    def register_attendee(self, db: Session, *, session_id: int) -> bool:
        """
        Incrementar el contador de asistentes registrados en una sesión
        """
        session = self.get(db, id=session_id)
        if not session:
            return False
        
        if session.registered_attendees >= session.capacity:
            return False
        
        session.registered_attendees += 1
        db.add(session)
        db.commit()
        return True
    
    def unregister_attendee(self, db: Session, *, session_id: int) -> bool:
        """
        Decrementar el contador de asistentes registrados en una sesión
        """
        session = self.get(db, id=session_id)
        if not session:
            return False
        
        if session.registered_attendees > 0:
            session.registered_attendees -= 1
            db.add(session)
            db.commit()
            return True
        
        return False


session_repository = SessionRepository(Session)