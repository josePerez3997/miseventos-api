from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

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
        # Update event statuses before searching
        event_repository.update_status(self.db)
        
        # Perform search with all parameters
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
        # Convertir esquema a diccionario
        event_data = event_in.model_dump()
        event_data["organizer_id"] = organizer_id
        event_data["registered_attendees"] = 0
        
        # Obtener usuario organizador para validaciones
        user = user_repository.get(self.db, id=organizer_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Validar datos del evento
        is_valid, error_msg = self.validation_service.validate_event_create(event_data, user)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Crear evento
        return event_repository.create(self.db, obj_in=event_data)
    
    def update_event(
        self, 
        event_id: int, 
        event_in: Union[EventUpdate, Dict[str, Any]], 
        user_id: int
    ) -> Optional[Event]:
        """
        Update an event with validations
        
        Parameters:
        - event_id: ID of the event to update
        - event_in: EventUpdate object or dictionary with fields to update
        - user_id: ID of the user attempting to update
        
        Raises:
        - HTTPException: If validation fails
        """
        # Convertir a diccionario si es un objeto Pydantic
        if hasattr(event_in, 'model_dump'):
            update_data = event_in.model_dump(exclude_unset=True)
        else:
            # Si ya es un diccionario, usarlo directamente
            update_data = event_in
        
        # Obtener usuario para validaciones
        user = user_repository.get(self.db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Validar actualización
        is_valid, error_msg = self.validation_service.validate_event_update(
            event_id, update_data, user
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Obtener evento para actualizar
        event = self.get_event(event_id)
        if not event:
            return None
        
        # Actualizar evento
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
            
        # Verificar permisos
        if event.organizer_id != user_id and user.role != "ADMIN":
            return False
        
        # No permitir eliminar eventos que ya han comenzado o tienen asistentes
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
        # Validar registro
        is_valid, error_msg = self.validation_service.validate_user_registration(
            event_id, user_id
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Verificar si ya está registrado
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
        
        # Crear registro
        registration = EventAttendee(
            event_id=event_id,
            user_id=user_id
        )
        
        self.db.add(registration)
        
        # Incrementar contador de asistentes
        event_repository.register_attendee(self.db, event_id=event_id)
        
        self.db.commit()
        return True
    
    def unregister_from_event(self, event_id: int, user_id: int) -> bool:
        """
        Unregister a user from an event with validations
        
        Raises:
        - HTTPException: If validation fails
        """
        # Validar baja de registro
        is_valid, error_msg = self.validation_service.validate_user_unregistration(
            event_id, user_id
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Verificar si está registrado
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
        
        # Eliminar registro
        self.db.delete(registration)
        
        # Decrementar contador de asistentes
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
    
    # Métodos de métricas
    
    def get_event_stats(self, event_id: int) -> Dict[str, Any]:
        """
        Get detailed statistics for a single event
        """
        event = self.get_event(event_id)
        if not event:
            return {}
        
        # Información básica del evento
        basic_info = {
            "id": event.id,
            "name": event.name,
            "date": event.date,
            "status": event.status,
            "registered_attendees": event.registered_attendees,
            "capacity": event.capacity,
            "occupation_percentage": round((event.registered_attendees / event.capacity) * 100, 2) if event.capacity > 0 else 0
        }
        
        # Registros por día
        registrations = (
            self.db.query(
                func.date(EventAttendee.registered_at).label('date'),
                func.count().label('count')
            )
            .filter(EventAttendee.event_id == event_id)
            .group_by(func.date(EventAttendee.registered_at))
            .order_by(func.date(EventAttendee.registered_at))
            .all()
        )
        
        registrations_by_day = [
            {"date": reg.date, "count": reg.count}
            for reg in registrations
        ]
        
        # Sesiones más populares
        from app.models.session import Session as EventSession
        from sqlalchemy import func, desc
        
        popular_sessions = (
            self.db.query(
                EventSession.id,
                EventSession.title,
                EventSession.start_time,
                EventSession.end_time,
                EventSession.registered_attendees,
                EventSession.capacity
            )
            .filter(EventSession.event_id == event_id)
            .order_by(desc(EventSession.registered_attendees))
            .all()
        )
        
        popular_sessions_data = [
            {
                "id": session.id,
                "title": session.title,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "registered_attendees": session.registered_attendees,
                "capacity": session.capacity,
                "occupation_percentage": round((session.registered_attendees / session.capacity) * 100, 2) if session.capacity > 0 else 0
            }
            for session in popular_sessions
        ]
        
        return {
            "basic_info": basic_info,
            "registrations_by_day": registrations_by_day,
            "popular_sessions": popular_sessions_data,
            "total_sessions": len(popular_sessions)
        }
    
    def get_upcoming_events_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get statistics for upcoming events in the next X days
        """
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        # Eventos próximos
        upcoming_events = (
            self.db.query(Event)
            .filter(
                Event.date >= now,
                Event.date <= end_date,
                Event.status == EventStatus.UPCOMING
            )
            .order_by(Event.date)
            .all()
        )
        
        events_data = [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "days_until_start": (event.date.date() - now.date()).days,
                "registered_attendees": event.registered_attendees,
                "capacity": event.capacity,
                "occupation_percentage": round((event.registered_attendees / event.capacity) * 100, 2) if event.capacity > 0 else 0
            }
            for event in upcoming_events
        ]
        
        # Estadísticas agregadas
        total_capacity = sum(event.capacity for event in upcoming_events)
        total_registered = sum(event.registered_attendees for event in upcoming_events)
        
        return {
            "upcoming_events": events_data,
            "total_upcoming_events": len(upcoming_events),
            "total_capacity": total_capacity,
            "total_registered": total_registered,
            "overall_occupation_percentage": round((total_registered / total_capacity) * 100, 2) if total_capacity > 0 else 0,
            "period_days": days,
            "start_date": now,
            "end_date": end_date
        }
    
    def get_organizer_event_stats(self, organizer_id: int) -> Dict[str, Any]:
        """
        Get statistics for events organized by a specific user
        """
        # Todos los eventos del organizador
        events = self.get_events_by_organizer(organizer_id)
        
        # Eventos por estado
        events_by_status = {}
        for status in EventStatus:
            count = sum(1 for event in events if event.status == status)
            events_by_status[status] = count
        
        # Eventos más populares
        sorted_events = sorted(events, key=lambda e: e.registered_attendees, reverse=True)
        top_events = sorted_events[:5]
        
        top_events_data = [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "status": event.status,
                "registered_attendees": event.registered_attendees,
                "capacity": event.capacity,
                "occupation_percentage": round((event.registered_attendees / event.capacity) * 100, 2) if event.capacity > 0 else 0
            }
            for event in top_events
        ]
        
        # Estadísticas agregadas
        total_attendees = sum(event.registered_attendees for event in events)
        total_capacity = sum(event.capacity for event in events)
        
        return {
            "total_events": len(events),
            "events_by_status": events_by_status,
            "top_events": top_events_data,
            "total_attendees": total_attendees,
            "total_capacity": total_capacity,
            "overall_occupation_percentage": round((total_attendees / total_capacity) * 100, 2) if total_capacity > 0 else 0
        }