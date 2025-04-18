from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_database
from app.repositories.event_repository import event_repository
from app.repositories.session_repository import session_repository
from app.models.event import Event, EventStatus
from app.models.session import Session as EventSession
from app.models.user import User, UserRole
from app.models.speaker import Speaker

class ValidationService:
    """
    Servicio para validaciones avanzadas de negocio
    """
    def __init__(self, db: Session = Depends(get_database)):
        self.db = db
    
    def validate_event_create(self, event_data: Dict[str, Any], user: User) -> Tuple[bool, str]:
        """
        Validar la creación de un evento
        
        Args:
            event_data: Datos del evento a crear
            user: Usuario que intenta crear el evento
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        if user.role != UserRole.ORGANIZER and user.role != UserRole.ADMIN:
            return False, "Solo los organizadores y administradores pueden crear eventos"
        
        current_date = datetime.now().date()
        event_date = event_data.get("date")
        
        if event_date and event_date.date() < current_date:
            return False, "La fecha del evento no puede ser en el pasado"
        
        end_date = event_data.get("end_date")
        if end_date and event_date and end_date < event_date:
            return False, "La fecha de fin debe ser posterior a la fecha de inicio"
        
        capacity = event_data.get("capacity")
        if capacity is not None and capacity <= 0:
            return False, "La capacidad debe ser un número positivo"
        
        name = event_data.get("name", "")
        description = event_data.get("description", "")
        
        if len(name) < 5:
            return False, "El nombre del evento debe tener al menos 5 caracteres"
            
        if len(description) < 20:
            return False, "La descripción del evento debe tener al menos 20 caracteres"
        
        return True, ""
    
    def validate_event_update(
        self, 
        event_id: int, 
        update_data: Dict[str, Any], 
        user: User
    ) -> Tuple[bool, str]:
        """
        Validar la actualización de un evento
        
        Args:
            event_id: ID del evento a actualizar
            update_data: Datos a actualizar
            user: Usuario que intenta actualizar el evento
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        event = event_repository.get(self.db, id=event_id)
        if not event:
            return False, "Evento no encontrado"
        
        if event.organizer_id != user.id and user.role != UserRole.ADMIN:
            return False, "No tienes permiso para actualizar este evento"
        
        if event.status in [EventStatus.CANCELLED, EventStatus.COMPLETED]:
            return False, f"No se puede modificar un evento con estado {event.status}"
        
        event_date = update_data.get("date")
        if event_date:
            current_date = datetime.now().date()
            
            if (event.status == EventStatus.ONGOING or 
                event.date.date() == current_date) and event_date.date() != event.date.date():
                return False, "No se puede cambiar la fecha de un evento en progreso o que comienza hoy"
                
            if event_date.date() < current_date:
                return False, "La fecha del evento no puede ser en el pasado"
        
        end_date = update_data.get("end_date")
        if end_date:
            start_date = event_date if event_date else event.date
            if end_date < start_date:
                return False, "La fecha de fin debe ser posterior a la fecha de inicio"
        
        capacity = update_data.get("capacity")
        if capacity is not None:
            if capacity <= 0:
                return False, "La capacidad debe ser un número positivo"
            
            if capacity < event.registered_attendees:
                return False, f"La capacidad no puede ser menor que el número de asistentes registrados ({event.registered_attendees})"
        
        status = update_data.get("status")
        if status:
            valid_transitions = {
                EventStatus.UPCOMING: [EventStatus.ONGOING, EventStatus.CANCELLED],
                EventStatus.ONGOING: [EventStatus.COMPLETED, EventStatus.CANCELLED],
                EventStatus.COMPLETED: [],  
                EventStatus.CANCELLED: [EventStatus.UPCOMING]  
            }
            
            if status not in valid_transitions.get(event.status, []):
                return False, f"No se puede cambiar el estado de {event.status} a {status}"
        
        name = update_data.get("name")
        if name is not None and len(name) < 5:
            return False, "El nombre del evento debe tener al menos 5 caracteres"
            
        description = update_data.get("description")
        if description is not None and len(description) < 20:
            return False, "La descripción del evento debe tener al menos 20 caracteres"
        
        return True, ""
    
    def validate_session_create(
        self, 
        session_data: Dict[str, Any], 
        user: User
    ) -> Tuple[bool, str]:
        """
        Validar la creación de una sesión
        
        Args:
            session_data: Datos de la sesión a crear
            user: Usuario que intenta crear la sesión
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        event_id = session_data.get("event_id")
        event = event_repository.get(self.db, id=event_id)
        if not event:
            return False, "Evento no encontrado"
        
        if event.organizer_id != user.id and user.role != UserRole.ADMIN:
            return False, "No tienes permiso para crear sesiones en este evento"
        
        if event.status in [EventStatus.COMPLETED, EventStatus.CANCELLED]:
            return False, f"No se pueden añadir sesiones a un evento con estado {event.status}"
        
        start_time = session_data.get("start_time")
        end_time = session_data.get("end_time")
        
        if start_time and end_time:
            if start_time >= end_time:
                return False, "La hora de inicio debe ser anterior a la hora de fin"
            
            event_start = datetime.combine(event.date, datetime.min.time())
            event_end = datetime.combine(event.end_date if event.end_date else event.date, datetime.max.time())
            
            if start_time < event_start:
                return False, "La sesión no puede comenzar antes que el evento"
                
            if end_time > event_end:
                return False, "La sesión no puede terminar después que el evento"
            
            has_conflict = session_repository.check_time_conflict(
                self.db, 
                event_id=event_id, 
                start_time=start_time, 
                end_time=end_time
            )
            
            if has_conflict:
                return False, "La sesión tiene conflicto de horario con otra sesión del evento"
        
        capacity = session_data.get("capacity")
        if capacity is not None:
            if capacity <= 0:
                return False, "La capacidad debe ser un número positivo"
            
            if capacity > event.capacity:
                return False, f"La capacidad de la sesión no puede ser mayor que la del evento ({event.capacity})"
        
        speaker_id = session_data.get("speaker_id")
        if speaker_id:
            speaker = self.db.query(Speaker).get(speaker_id)
            if not speaker:
                return False, "El ponente seleccionado no existe"
        
        title = session_data.get("title", "")
        description = session_data.get("description", "")
        
        if len(title) < 5:
            return False, "El título de la sesión debe tener al menos 5 caracteres"
            
        if len(description) < 20:
            return False, "La descripción de la sesión debe tener al menos 20 caracteres"
        
        return True, ""
    
    def validate_session_update(
        self, 
        session_id: int, 
        update_data: Dict[str, Any], 
        user: User
    ) -> Tuple[bool, str]:
        """
        Validar la actualización de una sesión
        
        Args:
            session_id: ID de la sesión a actualizar
            update_data: Datos a actualizar
            user: Usuario que intenta actualizar la sesión
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        session = session_repository.get(self.db, id=session_id)
        if not session:
            return False, "Sesión no encontrada"
        
        event = event_repository.get(self.db, id=session.event_id)
        if not event:
            return False, "Evento no encontrado"
        
        if event.organizer_id != user.id and user.role != UserRole.ADMIN:
            return False, "No tienes permiso para modificar sesiones en este evento"
        
        if event.status in [EventStatus.COMPLETED, EventStatus.CANCELLED]:
            return False, f"No se pueden modificar sesiones de un evento con estado {event.status}"
        
        start_time = update_data.get("start_time")
        end_time = update_data.get("end_time")
        
        if start_time or end_time:
            effective_start = start_time if start_time else session.start_time
            effective_end = end_time if end_time else session.end_time
            
            if effective_start >= effective_end:
                return False, "La hora de inicio debe ser anterior a la hora de fin"
            
            event_start = datetime.combine(event.date, datetime.min.time())
            event_end = datetime.combine(event.end_date if event.end_date else event.date, datetime.max.time())
            
            if effective_start < event_start:
                return False, "La sesión no puede comenzar antes que el evento"
                
            if effective_end > event_end:
                return False, "La sesión no puede terminar después que el evento"
            
            if start_time or end_time:  
                has_conflict = session_repository.check_time_conflict(
                    self.db, 
                    event_id=session.event_id, 
                    start_time=effective_start, 
                    end_time=effective_end,
                    session_id=session.id  
                )
                
                if has_conflict:
                    return False, "La sesión tiene conflicto de horario con otra sesión del evento"
        
        capacity = update_data.get("capacity")
        if capacity is not None:
            if capacity <= 0:
                return False, "La capacidad debe ser un número positivo"
            
            if capacity < session.registered_attendees:
                return False, f"La capacidad no puede ser menor que el número de asistentes registrados ({session.registered_attendees})"
            
            if capacity > event.capacity:
                return False, f"La capacidad de la sesión no puede ser mayor que la del evento ({event.capacity})"
        
        speaker_id = update_data.get("speaker_id")
        if speaker_id:
            speaker = self.db.query(Speaker).get(speaker_id)
            if not speaker:
                return False, "El ponente seleccionado no existe"
        
        title = update_data.get("title")
        if title is not None and len(title) < 5:
            return False, "El título de la sesión debe tener al menos 5 caracteres"
            
        description = update_data.get("description")
        if description is not None and len(description) < 20:
            return False, "La descripción de la sesión debe tener al menos 20 caracteres"
        
        return True, ""
    
    def validate_user_registration(
        self, 
        event_id: int, 
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Validar el registro de un usuario a un evento
        
        Args:
            event_id: ID del evento
            user_id: ID del usuario
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        event = event_repository.get(self.db, id=event_id)
        if not event:
            return False, "Evento no encontrado"
        
        if event.status not in [EventStatus.UPCOMING, EventStatus.ONGOING]:
            return False, f"No es posible registrarse a un evento con estado {event.status}"
        
        if event.registered_attendees >= event.capacity:
            return False, "El evento ha alcanzado su capacidad máxima"
        
        is_registered = any(
            attendee.user_id == user_id for attendee in event.attendees
        )
        
        if is_registered:
            return False, "El usuario ya está registrado en este evento"
        
        return True, ""
    
    def validate_user_unregistration(
        self, 
        event_id: int, 
        user_id: int
    ) -> Tuple[bool, str]:
        """
        Validar la cancelación de registro de un usuario a un evento
        
        Args:
            event_id: ID del evento
            user_id: ID del usuario
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        event = event_repository.get(self.db, id=event_id)
        if not event:
            return False, "Evento no encontrado"
        
        if event.status not in [EventStatus.UPCOMING, EventStatus.ONGOING]:
            return False, f"No es posible cancelar registro en un evento con estado {event.status}"
        
        if event.status == EventStatus.UPCOMING:
            now = datetime.now()
            event_start = datetime.combine(event.date, datetime.min.time())
            
            if (event_start - now).total_seconds() < 86400:  
                return False, "No es posible cancelar registro para eventos que comienzan en menos de 24 horas"
        
        is_registered = any(
            attendee.user_id == user_id for attendee in event.attendees
        )
        
        if not is_registered:
            return False, "El usuario no está registrado en este evento"
        
        return True, ""