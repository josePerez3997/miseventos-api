from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from app.api.dependencies.auth import get_current_active_user, get_current_active_superuser, get_optional_current_user
from app.models.user import User
from app.services.metrics_service import MetricsService
from app.repositories.user_repository import user_repository

router = APIRouter()

@router.get("/summary", response_model=Dict[str, Any])
def get_platform_summary(
    current_user: User = Depends(get_current_active_superuser),
    metrics_service: MetricsService = Depends(),
):
    """
    Obtener un resumen general de métricas de la plataforma (solo para administradores)
    """
    return metrics_service.get_platform_summary()

@router.get("/events", response_model=Dict[str, Any])
def get_events_metrics(
    metrics_service: MetricsService = Depends(),
):
    """
    Obtener métricas generales de eventos
    """
    return metrics_service.get_events_metrics()

@router.get("/events/{event_id}", response_model=Dict[str, Any])
def get_event_metrics(
    event_id: int = Path(..., ge=1),
    current_user: Optional[User] = Depends(get_optional_current_user),
    metrics_service: MetricsService = Depends(),
):
    """
    Obtener métricas detalladas para un evento específico
    """
    metrics = metrics_service.get_event_metrics(event_id=event_id)
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    
    return metrics

@router.get("/organizers/{user_id}", response_model=Dict[str, Any])
def get_organizer_metrics(
    user_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_active_user),
    metrics_service: MetricsService = Depends(),
):
    """
    Obtener métricas para un organizador específico
    
    Solo el propio organizador o un administrador pueden ver estas métricas
    """
    if current_user.id != user_id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estas métricas"
        )
    
    user = user_repository.get(current_user.db, id=user_id)
    if not user or user.role != "ORGANIZER":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es un organizador"
        )
    
    metrics = metrics_service.get_organizer_metrics(user_id=user_id)
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return metrics

@router.get("/users/me/attendance", response_model=Dict[str, Any])
def get_my_attendance_metrics(
    current_user: User = Depends(get_current_active_user),
    metrics_service: MetricsService = Depends(),
):
    """
    Obtener métricas de asistencia para el usuario actual
    """
    return metrics_service.get_user_attendance_metrics(user_id=current_user.id)

@router.get("/users/{user_id}/attendance", response_model=Dict[str, Any])
def get_user_attendance_metrics(
    user_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_active_user),
    metrics_service: MetricsService = Depends(),
):
    """
    Obtener métricas de asistencia para un usuario específico
    
    Solo el propio usuario o un administrador pueden ver estas métricas
    """
    if current_user.id != user_id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estas métricas"
        )
    
    metrics = metrics_service.get_user_attendance_metrics(user_id=user_id)
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return metrics

@router.get("/time-series", response_model=Dict[str, Any])
def get_time_series_metrics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_superuser),
    metrics_service: MetricsService = Depends(),
):
    """
    Obtener métricas de series temporales para los últimos 'days' días (solo para administradores)
    """
    return metrics_service.get_time_series_metrics(days=days)