from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import or_, and_, desc, func
from sqlalchemy.orm import Session, joinedload
from typing import Union
from app.models.event import Event, EventStatus
from app.models.category import Category, event_category
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
    
    def get(self, db: Session, id: Any) -> Optional[Event]:
        """
        Get an event by ID with categories loaded
        """
        return db.query(Event).options(joinedload(Event.categories)).filter(Event.id == id).first()
    
    def search(
        self, 
        db: Session, 
        *, 
        params: EventSearchParams,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search events with advanced filters including categories
        """
        query = db.query(Event).options(joinedload(Event.categories))
        
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
        
        if params.location:
            query = query.filter(Event.location.ilike(f"%{params.location}%"))
        
        if params.organizer_id:
            query = query.filter(Event.organizer_id == params.organizer_id)
        elif user_id:
            query = query.filter(Event.organizer_id == user_id)
            
        if params.category_id:
            query = query.join(event_category).join(Category).filter(Category.id == params.category_id)
            
        if params.category_ids and len(params.category_ids) > 0:
            for category_id in params.category_ids:
                subquery = db.query(event_category.c.event_id).filter(event_category.c.category_id == category_id).scalar_subquery()
                query = query.filter(Event.id.in_(subquery))
        
        if params.date_from:
            query = query.filter(Event.date >= params.date_from)
        
        if params.date_to:
            query = query.filter(Event.date <= params.date_to)
        
        if params.min_capacity:
            query = query.filter(Event.capacity >= params.min_capacity)
        
        if params.max_capacity:
            query = query.filter(Event.capacity <= params.max_capacity)
        
        if params.has_available_spots:
            query = query.filter(Event.registered_attendees < Event.capacity)
        
        total = query.count()
        
        if params.sort_by:
            sort_field_map = {
                'date': Event.date,
                'name': Event.name,
                'popularity': Event.registered_attendees,
                'capacity': Event.capacity
            }
            
            sort_field = sort_field_map.get(params.sort_by, Event.date)
            
            if params.sort_order and params.sort_order.lower() == 'desc':
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(sort_field)
        else:
            query = query.order_by(Event.date)
        
        pages = (total + params.size - 1) // params.size if total > 0 else 0
        page = min(params.page, pages) if pages > 0 else 1
        skip = (page - 1) * params.size
        
        events = query.offset(skip).limit(params.size).all()
        
        return {
            "items": events,
            "total": total,
            "page": page,
            "size": params.size,
            "pages": pages
        }
    
    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> Event:
        """
        Create a new event with categories
        """
        category_ids = obj_in.pop("category_ids", []) or []
        
        db_obj = self.model(**obj_in)
        
        if category_ids:
            categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
            db_obj.categories = categories
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Event,
        obj_in: Union[EventUpdate, Dict[str, Any]]
    ) -> Event:
        """
        Update an event including categories
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        category_ids = update_data.pop("category_ids", None)
        
        for field in update_data:
            if field != "categories" and field in update_data:
                setattr(db_obj, field, update_data[field])
                
        if category_ids is not None:
            categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
            db_obj.categories = categories
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
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
        
    def get_events_by_category(self, db: Session, *, category_id: int) -> List[Event]:
        """
        Get events by category ID
        """
        return (
            db.query(Event)
            .join(event_category)
            .filter(event_category.c.category_id == category_id)
            .all()
        )


event_repository = EventRepository(Event)