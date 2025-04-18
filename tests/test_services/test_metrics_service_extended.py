import pytest
from datetime import datetime, timedelta
from app.services.metrics_service import MetricsService
from app.models.event_attendee import EventAttendee
from app.models.user import User

class TestMetricsServiceExtended:
    
    def test_get_platform_summary(self, db_session, test_admin):
        """Test para obtener resumen de la plataforma"""
        metrics_service = MetricsService(db=db_session)
        
        summary = metrics_service.get_platform_summary()
        
        assert summary is not None
        assert "total_events" in summary
        assert "total_users" in summary
        assert "total_sessions" in summary
        assert "events_by_status" in summary
        assert "users_by_role" in summary
    
    def test_get_organizer_metrics(self, db_session, test_organizer, test_event):
        """Test para obtener métricas de organizador"""
        metrics_service = MetricsService(db=db_session)
        
        metrics = metrics_service.get_organizer_metrics(user_id=test_organizer.id)
        
        assert metrics is not None
        assert "basic_info" in metrics
        assert metrics["basic_info"]["id"] == test_organizer.id
        assert "events" in metrics
    
    def test_get_time_series_metrics(self, db_session):
        """Test para obtener métricas de series temporales"""
        metrics_service = MetricsService(db=db_session)
        
        metrics = metrics_service.get_time_series_metrics(days=30)
        
        assert metrics is not None
        assert "events_by_day" in metrics
        assert "users_by_day" in metrics
        assert "registrations_by_day" in metrics
        assert "start_date" in metrics
        assert "end_date" in metrics
        assert "days" in metrics
        assert metrics["days"] == 30