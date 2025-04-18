from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

from fastapi import Depends
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_database
from app.models.event import Event, EventStatus
from app.models.event_attendee import EventAttendee
from app.models.session import Session as EventSession
from app.models.session_attendee import SessionAttendee
from app.models.user import User, UserRole
from app.repositories.event_repository import event_repository
from app.repositories.user_repository import user_repository

class MetricsService:
    """
    Servicio para obtener métricas y estadísticas sobre eventos, sesiones y asistentes
    """
    def __init__(self, db: Session = Depends(get_database)):
        self.db = db
    
    def get_platform_summary(self) -> Dict[str, Any]:
        """
        Obtener un resumen general de la plataforma
        """
        total_events = self.db.query(func.count(Event.id)).scalar() or 0
        total_users = self.db.query(func.count(User.id)).scalar() or 0
        total_sessions = self.db.query(func.count(EventSession.id)).scalar() or 0
        
        events_by_status = {}
        for status in EventStatus:
            count = self.db.query(func.count(Event.id)).filter(Event.status == status).scalar() or 0
            events_by_status[status] = count
        
        users_by_role = {}
        for role in UserRole:
            count = self.db.query(func.count(User.id)).filter(User.role == role).scalar() or 0
            users_by_role[role] = count
        
        total_event_registrations = self.db.query(func.count(EventAttendee.id)).scalar() or 0
        total_session_registrations = self.db.query(func.count(SessionAttendee.id)).scalar() or 0
        
        upcoming_events = self.db.query(func.count(Event.id)).filter(
            Event.status == EventStatus.UPCOMING
        ).scalar() or 0
        
        ongoing_events = self.db.query(func.count(Event.id)).filter(
            Event.status == EventStatus.ONGOING
        ).scalar() or 0
        
        return {
            "total_events": total_events,
            "total_users": total_users,
            "total_sessions": total_sessions,
            "events_by_status": events_by_status,
            "users_by_role": users_by_role,
            "total_event_registrations": total_event_registrations,
            "total_session_registrations": total_session_registrations,
            "upcoming_events": upcoming_events,
            "ongoing_events": ongoing_events
        }
    
    def get_events_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas generales de eventos
        """
        total_events = self.db.query(func.count(Event.id)).scalar() or 0
        
        events_by_status = {}
        for status in EventStatus:
            count = self.db.query(func.count(Event.id)).filter(Event.status == status).scalar() or 0
            events_by_status[status] = count
        
        popular_events = self.db.query(
            Event.id, Event.name, Event.date, Event.status, 
            Event.registered_attendees, Event.capacity
        ).order_by(
            desc(Event.registered_attendees)
        ).limit(10).all()
        
        popular_events_list = [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "status": event.status,
                "registered_attendees": event.registered_attendees,
                "capacity": event.capacity,
                "occupation_percentage": round((event.registered_attendees / event.capacity) * 100, 2) if event.capacity > 0 else 0
            }
            for event in popular_events
        ]
        
        highest_occupation_events = self.db.query(
            Event.id, Event.name, Event.date, Event.status, 
            Event.registered_attendees, Event.capacity
        ).filter(
            Event.capacity > 0
        ).all()
        
        highest_occupation_events = sorted(
            highest_occupation_events,
            key=lambda e: (e.registered_attendees / e.capacity),
            reverse=True
        )[:10]
        
        occupation_events_list = [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "status": event.status,
                "registered_attendees": event.registered_attendees,
                "capacity": event.capacity,
                "occupation_percentage": round((event.registered_attendees / event.capacity) * 100, 2)
            }
            for event in highest_occupation_events
        ]
        
        now = datetime.now()
        upcoming_events = self.db.query(
            Event.id, Event.name, Event.date, Event.registered_attendees, Event.capacity
        ).filter(
            Event.status == EventStatus.UPCOMING,
            Event.date > now
        ).order_by(
            Event.date
        ).limit(10).all()
        
        upcoming_events_list = [
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
        
        events_by_month = self.db.query(
            func.extract('month', Event.date).label('month'),
            func.extract('year', Event.date).label('year'),
            func.count(Event.id).label('count')
        ).group_by(
            func.extract('month', Event.date),
            func.extract('year', Event.date)
        ).all()
        
        events_by_month_list = [
            {
                "month": int(result.month),
                "year": int(result.year),
                "count": result.count
            }
            for result in events_by_month
        ]
        
        return {
            "total_events": total_events,
            "events_by_status": events_by_status,
            "popular_events": popular_events_list,
            "highest_occupation_events": occupation_events_list,
            "upcoming_events": upcoming_events_list,
            "events_by_month": events_by_month_list
        }
    
    def get_event_metrics(self, event_id: int) -> Dict[str, Any]:
        """
        Obtener métricas detalladas para un evento específico
        """
        event = event_repository.get(self.db, id=event_id)
        if not event:
            return {}
        
        basic_info = {
            "id": event.id,
            "name": event.name,
            "date": event.date,
            "end_date": event.end_date,
            "status": event.status,
            "registered_attendees": event.registered_attendees,
            "capacity": event.capacity,
            "location": event.location,
            "occupation_percentage": round((event.registered_attendees / event.capacity) * 100, 2) if event.capacity > 0 else 0
        }
        
        sessions = self.db.query(EventSession).filter(
            EventSession.event_id == event_id
        ).all()
        
        sessions_info = [
            {
                "id": session.id,
                "title": session.title,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "location": session.location,
                "registered_attendees": session.registered_attendees,
                "capacity": session.capacity,
                "occupation_percentage": round((session.registered_attendees / session.capacity) * 100, 2) if session.capacity > 0 else 0
            }
            for session in sessions
        ]
        
        attendees_count = self.db.query(func.count(EventAttendee.id)).filter(
            EventAttendee.event_id == event_id
        ).scalar() or 0
        
        attendees_by_day = self.db.query(
            func.date(EventAttendee.registered_at).label('date'),
            func.count(EventAttendee.id).label('count')
        ).filter(
            EventAttendee.event_id == event_id
        ).group_by(
            func.date(EventAttendee.registered_at)
        ).all()
        
        attendees_by_day_list = [
            {
                "date": result.date,
                "count": result.count
            }
            for result in attendees_by_day
        ]
        
        organizer_events = self.db.query(
            Event.id, Event.name, Event.registered_attendees
        ).filter(
            Event.organizer_id == event.organizer_id
        ).all()
        
        organizer_events_list = [
            {
                "id": e.id,
                "name": e.name,
                "registered_attendees": e.registered_attendees
            }
            for e in organizer_events
        ]
        
        sorted_by_attendees = sorted(organizer_events, key=lambda e: e.registered_attendees)
        position = next((i for i, e in enumerate(sorted_by_attendees) if e.id == event_id), -1)
        
        if position >= 0 and len(sorted_by_attendees) > 0:
            percentile = round((position / len(sorted_by_attendees)) * 100, 2)
        else:
            percentile = None
        
        return {
            "basic_info": basic_info,
            "sessions": sessions_info,
            "attendees_count": attendees_count,
            "attendees_by_day": attendees_by_day_list,
            "organizer_events": organizer_events_list,
            "popularity_percentile": percentile
        }
    
    def get_organizer_metrics(self, user_id: int) -> Dict[str, Any]:
        """
        Obtener métricas para un organizador específico
        """
        user = user_repository.get(self.db, id=user_id)
        if not user:
            return {}
        
        basic_info = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
        
        events = self.db.query(Event).filter(
            Event.organizer_id == user_id
        ).all()
        
        events_info = [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "status": event.status,
                "registered_attendees": event.registered_attendees,
                "capacity": event.capacity,
                "occupation_percentage": round((event.registered_attendees / event.capacity) * 100, 2) if event.capacity > 0 else 0
            }
            for event in events
        ]
        
        events_by_status = {}
        for status in EventStatus:
            count = self.db.query(func.count(Event.id)).filter(
                Event.organizer_id == user_id,
                Event.status == status
            ).scalar() or 0
            events_by_status[status] = count
        
        total_attendees = self.db.query(func.sum(Event.registered_attendees)).filter(
            Event.organizer_id == user_id
        ).scalar() or 0
        
        popular_events = self.db.query(
            Event.id, Event.name, Event.date, Event.status, 
            Event.registered_attendees, Event.capacity
        ).filter(
            Event.organizer_id == user_id
        ).order_by(
            desc(Event.registered_attendees)
        ).limit(5).all()
        
        popular_events_list = [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "status": event.status,
                "registered_attendees": event.registered_attendees,
                "capacity": event.capacity,
                "occupation_percentage": round((event.registered_attendees / event.capacity) * 100, 2) if event.capacity > 0 else 0
            }
            for event in popular_events
        ]
        
        organizer_attendees = {}
        organizers = self.db.query(
            Event.organizer_id, func.sum(Event.registered_attendees).label('total_attendees')
        ).group_by(
            Event.organizer_id
        ).all()
        
        for org in organizers:
            organizer_attendees[org.organizer_id] = org.total_attendees
        
        sorted_organizers = sorted(organizer_attendees.items(), key=lambda x: x[1])
        organizer_position = next((i for i, (org_id, _) in enumerate(sorted_organizers) if org_id == user_id), -1)
        
        if organizer_position >= 0 and len(sorted_organizers) > 0:
            percentile = round((organizer_position / len(sorted_organizers)) * 100, 2)
        else:
            percentile = None
        
        return {
            "basic_info": basic_info,
            "events": events_info,
            "events_by_status": events_by_status,
            "total_events": len(events),
            "total_attendees": total_attendees,
            "popular_events": popular_events_list,
            "organizer_percentile": percentile
        }
    
    def get_user_attendance_metrics(self, user_id: int) -> Dict[str, Any]:
        """
        Obtener métricas de asistencia para un usuario específico
        """
        user = user_repository.get(self.db, id=user_id)
        if not user:
            return {}
        
        basic_info = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
        
        attended_events = self.db.query(
            Event
        ).join(
            EventAttendee, Event.id == EventAttendee.event_id
        ).filter(
            EventAttendee.user_id == user_id
        ).all()
        
        events_info = [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "status": event.status,
                "registered_attendees": event.registered_attendees,
                "capacity": event.capacity
            }
            for event in attended_events
        ]
        
        events_by_status = {}
        for status in EventStatus:
            count = self.db.query(func.count(Event.id)).join(
                EventAttendee, Event.id == EventAttendee.event_id
            ).filter(
                EventAttendee.user_id == user_id,
                Event.status == status
            ).scalar() or 0
            events_by_status[status] = count
        
        attended_sessions = self.db.query(
            EventSession
        ).join(
            SessionAttendee, EventSession.id == SessionAttendee.session_id
        ).filter(
            SessionAttendee.user_id == user_id
        ).all()
        
        sessions_info = [
            {
                "id": session.id,
                "title": session.title,
                "event_id": session.event_id,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "location": session.location
            }
            for session in attended_sessions
        ]
        
        now = datetime.now()
        upcoming_events = self.db.query(
            Event
        ).join(
            EventAttendee, Event.id == EventAttendee.event_id
        ).filter(
            EventAttendee.user_id == user_id,
            Event.date > now
        ).order_by(
            Event.date
        ).all()
        
        upcoming_events_info = [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "days_until_start": (event.date.date() - now.date()).days
            }
            for event in upcoming_events
        ]
        
        upcoming_sessions = self.db.query(
            EventSession
        ).join(
            SessionAttendee, EventSession.id == SessionAttendee.session_id
        ).filter(
            SessionAttendee.user_id == user_id,
            EventSession.start_time > now
        ).order_by(
            EventSession.start_time
        ).all()
        
        upcoming_sessions_info = [
            {
                "id": session.id,
                "title": session.title,
                "event_id": session.event_id,
                "start_time": session.start_time,
                "hours_until_start": round((session.start_time - now).total_seconds() / 3600, 1)
            }
            for session in upcoming_sessions
        ]
        
        return {
            "basic_info": basic_info,
            "attended_events": events_info,
            "events_by_status": events_by_status,
            "total_attended_events": len(attended_events),
            "attended_sessions": sessions_info,
            "total_attended_sessions": len(attended_sessions),
            "upcoming_events": upcoming_events_info,
            "upcoming_sessions": upcoming_sessions_info
        }
    
    def get_time_series_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtener métricas de series temporales para los últimos 'days' días
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        events_by_day = self.db.query(
            func.date(Event.created_at).label('date'),
            func.count(Event.id).label('count')
        ).filter(
            Event.created_at >= start_date
        ).group_by(
            func.date(Event.created_at)
        ).all()
        
        events_by_day_list = [
            {
                "date": result.date,
                "count": result.count
            }
            for result in events_by_day
        ]
        
        users_by_day = self.db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(
            func.date(User.created_at)
        ).all()
        
        users_by_day_list = [
            {
                "date": result.date,
                "count": result.count
            }
            for result in users_by_day
        ]
        
        registrations_by_day = self.db.query(
            func.date(EventAttendee.registered_at).label('date'),
            func.count(EventAttendee.id).label('count')
        ).filter(
            EventAttendee.registered_at >= start_date
        ).group_by(
            func.date(EventAttendee.registered_at)
        ).all()
        
        registrations_by_day_list = [
            {
                "date": result.date,
                "count": result.count
            }
            for result in registrations_by_day
        ]
        
        return {
            "events_by_day": events_by_day_list,
            "users_by_day": users_by_day_list,
            "registrations_by_day": registrations_by_day_list,
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        }