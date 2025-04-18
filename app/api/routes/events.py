from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user, get_optional_current_user
from app.models.user import User
from app.services.event_service import EventService
from app.schemas.event import (
    Event, EventCreate, EventUpdate, EventPage, 
    EventWithOrganizer, EventSearchParams, EventStatus
)

router = APIRouter()

@router.get("", response_model=EventPage)
def get_events(
    search: Optional[str] = None,
    status: Optional[EventStatus] = None,
    location: Optional[str] = None,
    organizer_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_capacity: Optional[int] = None,
    max_capacity: Optional[int] = None,
    has_available_spots: Optional[bool] = None,
    sort_by: Optional[str] = "date",
    sort_order: Optional[str] = "asc",
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    event_service: EventService = Depends(),
):
    """
    Get events with advanced search filters
    
    - **search**: Search in name, description, and location
    - **status**: Filter by event status (UPCOMING, ONGOING, COMPLETED, CANCELLED)
    - **location**: Filter by location (partial match)
    - **organizer_id**: Filter by organizer ID
    - **date_from**: Filter events starting from this date (ISO format)
    - **date_to**: Filter events up to this date (ISO format)
    - **min_capacity**: Filter by minimum capacity
    - **max_capacity**: Filter by maximum capacity
    - **has_available_spots**: Filter for events that have spots available
    - **sort_by**: Sort by field (date, name, popularity, capacity)
    - **sort_order**: Sort order (asc, desc)
    - **page**: Page number (starts at 1)
    - **size**: Page size (items per page)
    """
    from datetime import datetime
    parsed_date_from = datetime.fromisoformat(date_from) if date_from else None
    parsed_date_to = datetime.fromisoformat(date_to) if date_to else None
    
    params = EventSearchParams(
        search=search,
        status=status,
        location=location,
        organizer_id=organizer_id,
        date_from=parsed_date_from,
        date_to=parsed_date_to,
        min_capacity=min_capacity,
        max_capacity=max_capacity,
        has_available_spots=has_available_spots,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        size=size
    )
    
    result = event_service.get_events(params=params)
    return result

@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    current_user: User = Depends(get_current_active_user),
    event_service: EventService = Depends(),
):
    """
    Create a new event (requires authentication)
    """
    event = event_service.create_event(
        event_in=event_in, 
        organizer_id=current_user.id
    )
    return event

@router.get("/my", response_model=List[Event])
def get_my_events(
    current_user: User = Depends(get_current_active_user),
    event_service: EventService = Depends(),
):
    """
    Get events organized by the current user
    """
    events = event_service.get_events_by_organizer(organizer_id=current_user.id)
    return events

@router.get("/registered", response_model=List[Event])
def get_registered_events(
    current_user: User = Depends(get_current_active_user),
    event_service: EventService = Depends(),
):
    """
    Get events that the current user is registered for
    """
    events = event_service.get_user_registered_events(user_id=current_user.id)
    return events

@router.get("/{event_id}", response_model=EventWithOrganizer)
def get_event(
    event_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    event_service: EventService = Depends(),
):
    """
    Get a specific event by ID
    """
    event = event_service.get_event(event_id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event

@router.put("/{event_id}", response_model=Event)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    event_service: EventService = Depends(),
):
    """
    Update an event (only for the organizer)
    """
    event = event_service.update_event(
        event_id=event_id, 
        event_in=event_in, 
        user_id=current_user.id
    )
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or permission denied",
        )
    return event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    event_service: EventService = Depends(),
):
    """
    Delete an event (only for the organizer)
    """
    success = event_service.delete_event(
        event_id=event_id, 
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or permission denied",
        )
    return None

@router.post("/{event_id}/register", status_code=status.HTTP_200_OK)
def register_for_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    event_service: EventService = Depends(),
):
    """
    Register current user for an event
    """
    success = event_service.register_for_event(
        event_id=event_id, 
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to register for event (event full, already registered, or not available)",
        )
    return {"success": True, "message": "Registered successfully"}

@router.post("/{event_id}/unregister", status_code=status.HTTP_200_OK)
def unregister_from_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    event_service: EventService = Depends(),
):
    """
    Unregister current user from an event
    """
    success = event_service.unregister_from_event(
        event_id=event_id, 
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to unregister from event (not registered or not available)",
        )
    return {"success": True, "message": "Unregistered successfully"}

@router.get("/{event_id}/registration-status", status_code=status.HTTP_200_OK)
def check_registration_status(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    event_service: EventService = Depends(),
):
    """
    Check if current user is registered for an event
    """
    is_registered = event_service.is_user_registered(
        event_id=event_id, 
        user_id=current_user.id
    )
    return {"is_registered": is_registered}