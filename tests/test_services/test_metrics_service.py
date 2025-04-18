import pytest
from app.services.metrics_service import MetricsService

class TestMetricsService:
    
    def test_get_events_metrics(self, db_session, test_event):
        """Test para obtener métricas generales de eventos"""
        metrics_service = MetricsService(db=db_session)
        
        metrics = metrics_service.get_events_metrics()
        
        assert metrics is not None
        assert "total_events" in metrics
        assert "events_by_status" in metrics
        assert "popular_events" in metrics
        assert metrics["total_events"] > 0
    
    def test_get_event_metrics(self, db_session, test_event):
        """Test para obtener métricas de un evento específico"""
        metrics_service = MetricsService(db=db_session)
        
        metrics = metrics_service.get_event_metrics(event_id=test_event.id)
        
        assert metrics is not None
        assert "basic_info" in metrics
        assert metrics["basic_info"]["id"] == test_event.id
        assert metrics["basic_info"]["name"] == test_event.name
    
    def test_get_user_attendance_metrics(self, db_session, test_user, test_event):
        """Test para obtener métricas de asistencia de un usuario"""
        metrics_service = MetricsService(db=db_session)
        
        # Registrar al usuario en el evento
        from app.models.event_attendee import EventAttendee
        attendee = EventAttendee(
            event_id=test_event.id,
            user_id=test_user.id
        )
        db_session.add(attendee)
        db_session.commit()
        
        metrics = metrics_service.get_user_attendance_metrics(user_id=test_user.id)
        
        assert metrics is not None
        assert "basic_info" in metrics
        assert metrics["basic_info"]["id"] == test_user.id
        assert "attended_events" in metrics
        assert len(metrics["attended_events"]) > 0
        assert metrics["attended_events"][0]["id"] == test_event.id