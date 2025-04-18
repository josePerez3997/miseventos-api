from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.models.event import Event, EventStatus
from app.schemas.event import EventCreate, EventUpdate, EventSearchParams
from app.repositories.base import BaseRepository

class EventRepository(BaseRepository[Event, EventCreate, EventUpdate]):
    """
    Repository for Event model with additional methods
    """
    def get_by_organizer(self, db: Session, *, organizer_id: int) -> List[Event]:
        """
        Get events by organizer
        """
        return db.query(Event).filter(Event.organizer_id == organizer_id).all()
    
    def search(
        self, 
        db: Session, 
        *, 
        params: EventSearchParams,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search events with filters
        """
        query = db.query(Event)
        
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    Event.name.ilike(search_term),
                    Event.description.ilike(search_term),
                    Event.location.ilike(search_term)
                )
            )
        
        if params.status:
            query = query.filter(Event.status == params.status)
        
        if params.date_from:
            query = query.filter(Event.date >= params.date_from)
        
        if params.date_to:
            query = query.filter(Event.date <= params.date_to)
        
        if user_id:
            query = query.filter(Event.organizer_id == user_id)
        
        total = query.count()
        
        pages = (total + params.size - 1) // params.size if total > 0 else 0
        page = min(params.page, pages) if pages > 0 else 1
        skip = (page - 1) * params.size
        
        events = query.order_by(Event.date).offset(skip).limit(params.size).all()
        
        return {
            "items": events,
            "total": total,
            "page": page,
            "size": params.size,
            "pages": pages
        }
    
    def register_attendee(self, db: Session, *, event_id: int) -> bool:
        """
        Incrementar el contador de asistentes registrados
        """
        event = self.get(db, id=event_id)
        if not event:
            return False
        
        if event.registered_attendees >= event.capacity:
            return False
        
        event.registered_attendees += 1
        db.add(event)
        db.commit()
        return True
    
    def unregister_attendee(self, db: Session, *, event_id: int) -> bool:
        """
        Decrementar el contador de asistentes registrados
        """
        event = self.get(db, id=event_id)
        if not event:
            return False
        
        if event.registered_attendees > 0:
            event.registered_attendees -= 1
            db.add(event)
            db.commit()
            return True
        
        return False
    
    def update_status(self, db: Session) -> None:
        """
        Actualizar el estado de los eventos según la fecha
        """
        today = datetime.utcnow()
        
        db.query(Event).filter(
            and_(
                Event.date <= today,
                or_(
                    Event.end_date == None,
                    Event.end_date >= today
                ),
                Event.status == EventStatus.UPCOMING
            )
        ).update({Event.status: EventStatus.ONGOING}, synchronize_session=False)
        
        db.query(Event).filter(
            and_(
                Event.end_date != None,
                Event.end_date < today,
                Event.status != EventStatus.CANCELLED,
                Event.status != EventStatus.COMPLETED
            )
        ).update({Event.status: EventStatus.COMPLETED}, synchronize_session=False)
        
        db.commit()


event_repository = EventRepository(Event)