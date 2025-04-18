from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_database
from app.repositories.event_repository import event_repository
from app.repositories.user_repository import user_repository
from app.models.event import Event, EventStatus
from app.schemas.event import EventCreate, EventUpdate, EventSearchParams
from app.models.event_attendee import EventAttendee
from app.services.validation_service import ValidationService

class EventService:
    """
    Service for event related operations
    """
    def __init__(
        self, 
        db: Session = Depends(get_database),
        validation_service: ValidationService = Depends()
    ):
        self.db = db
        self.validation_service = validation_service
    
    def get_event(self, event_id: int) -> Optional[Event]:
        """
        Get an event by ID
        """
        return event_repository.get(self.db, id=event_id)
    
    def get_events(
        self, 
        params: EventSearchParams,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get events with advanced filters
        
        Parameters:
        - params: EventSearchParams with all search filters
        - user_id: Optional user ID to filter events by organizer
        
        Returns:
        - Dictionary with paginated results and metadata
        """
        event_repository.update_status(self.db)
        
        return event_repository.search(self.db, params=params, user_id=user_id)
    
    def get_events_by_organizer(self, organizer_id: int) -> List[Event]:
        """
        Get events organized by a specific user
        """
        return event_repository.get_by_organizer(self.db, organizer_id=organizer_id)
    
    def create_event(self, event_in: EventCreate, organizer_id: int) -> Event:
        """
        Create a new event with validations
        
        Raises:
        - HTTPException: If validation fails
        """
        event_data = event_in.model_dump()
        event_data["organizer_id"] = organizer_id
        event_data["registered_attendees"] = 0
        
        user = user_repository.get(self.db, id=organizer_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        is_valid, error_msg = self.validation_service.validate_event_create(event_data, user)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        return event_repository.create(self.db, obj_in=event_data)
    
    def update_event(self, event_id: int, event_in: EventUpdate, user_id: int) -> Optional[Event]:
        """
        Update an event with validations
        
        Raises:
        - HTTPException: If validation fails
        """
        update_data = event_in.model_dump(exclude_unset=True)
        
        user = user_repository.get(self.db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        is_valid, error_msg = self.validation_service.validate_event_update(
            event_id, update_data, user
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        event = self.get_event(event_id)
        if not event:
            return None
        
        return event_repository.update(self.db, db_obj=event, obj_in=update_data)
    
    def delete_event(self, event_id: int, user_id: int) -> bool:
        """
        Delete an event if user is the organizer or admin
        
        Raises:
        - HTTPException: If validation fails
        """
        event = self.get_event(event_id)
        if not event:
            return False
        
        user = user_repository.get(self.db, id=user_id)
        if not user:
            return False
            
        if event.organizer_id != user_id and user.role != "ADMIN":
            return False
        
        if event.status != EventStatus.UPCOMING or event.registered_attendees > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un evento que ya ha comenzado o tiene asistentes registrados"
            )
        
        event_repository.remove(self.db, id=event_id)
        return True
    
    def register_for_event(self, event_id: int, user_id: int) -> bool:
        """
        Register a user for an event with validations
        
        Raises:
        - HTTPException: If validation fails
        """
        is_valid, error_msg = self.validation_service.validate_user_registration(
            event_id, user_id
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        existing_registration = (
            self.db.query(EventAttendee)
            .filter(
                EventAttendee.event_id == event_id,
                EventAttendee.user_id == user_id
            )
            .first()
        )
        
        if existing_registration:
            return True
        
        registration = EventAttendee(
            event_id=event_id,
            user_id=user_id
        )
        
        self.db.add(registration)
        
        event_repository.register_attendee(self.db, event_id=event_id)
        
        self.db.commit()
        return True
    
    def unregister_from_event(self, event_id: int, user_id: int) -> bool:
        """
        Unregister a user from an event with validations
        
        Raises:
        - HTTPException: If validation fails
        """
        is_valid, error_msg = self.validation_service.validate_user_unregistration(
            event_id, user_id
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        registration = (
            self.db.query(EventAttendee)
            .filter(
                EventAttendee.event_id == event_id,
                EventAttendee.user_id == user_id
            )
            .first()
        )
        
        if not registration:
            return False
        
        self.db.delete(registration)
        
        event_repository.unregister_attendee(self.db, event_id=event_id)
        
        self.db.commit()
        return True
    
    def get_user_registered_events(self, user_id: int) -> List[Event]:
        """
        Get events that a user is registered for
        """
        registrations = (
            self.db.query(EventAttendee)
            .filter(EventAttendee.user_id == user_id)
            .all()
        )
        
        event_ids = [reg.event_id for reg in registrations]
        
        if not event_ids:
            return []
        
        events = (
            self.db.query(Event)
            .filter(Event.id.in_(event_ids))
            .all()
        )
        
        return events
    
    def is_user_registered(self, event_id: int, user_id: int) -> bool:
        """
        Check if a user is registered for an event
        """
        registration = (
            self.db.query(EventAttendee)
            .filter(
                EventAttendee.event_id == event_id,
                EventAttendee.user_id == user_id
            )
            .first()
        )
        
        return registration is not None