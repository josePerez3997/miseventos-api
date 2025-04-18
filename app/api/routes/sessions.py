from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.session_service import SessionService
from app.schemas.session import Session, SessionCreate, SessionUpdate, SessionWithSpeaker

router = APIRouter()

@router.get("/event/{event_id}", response_model=List[SessionWithSpeaker])
def get_sessions_by_event(
    event_id: int,
    session_service: SessionService = Depends(),
):
    """
    Get all sessions for an event
    """
    sessions = session_service.get_sessions_by_event(event_id=event_id)
    return sessions

@router.post("", response_model=Session, status_code=status.HTTP_201_CREATED)
def create_session(
    session_in: SessionCreate,
    current_user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(),
):
    """
    Create a new session (only by event organizer)
    """
    session = session_service.create_session(
        session_in=session_in, 
        user_id=current_user.id
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create session (time conflict, or not event organizer)",
        )
    return session

@router.get("/{session_id}", response_model=SessionWithSpeaker)
def get_session(
    session_id: int,
    session_service: SessionService = Depends(),
):
    """
    Get a specific session by ID
    """
    session = session_service.get_session(session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session

@router.put("/{session_id}", response_model=Session)
def update_session(
    session_id: int,
    session_in: SessionUpdate,
    current_user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(),
):
    """
    Update a session (only by event organizer)
    """
    session = session_service.update_session(
        session_id=session_id, 
        session_in=session_in, 
        user_id=current_user.id
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update session (not found, time conflict, or not event organizer)",
        )
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(),
):
    """
    Delete a session (only by event organizer)
    """
    success = session_service.delete_session(
        session_id=session_id, 
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete session (not found or not event organizer)",
        )
    return None

@router.post("/{session_id}/register", status_code=status.HTTP_200_OK)
def register_for_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(),
):
    """
    Register current user for a session
    """
    success = session_service.register_for_session(
        session_id=session_id, 
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot register for session (session full or already registered)",
        )
    return {"success": True, "message": "Registered for session successfully"}

@router.post("/{session_id}/unregister", status_code=status.HTTP_200_OK)
def unregister_from_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(),
):
    """
    Unregister current user from a session
    """
    success = session_service.unregister_from_session(
        session_id=session_id, 
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unregister from session (not registered)",
        )
    return {"success": True, "message": "Unregistered from session successfully"}

@router.get("/{session_id}/registration-status", status_code=status.HTTP_200_OK)
def check_registration_status(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(),
):
    """
    Check if current user is registered for a session
    """
    is_registered = session_service.is_user_registered(
        session_id=session_id, 
        user_id=current_user.id
    )
    return {"is_registered": is_registered}

@router.get("/user/registered", response_model=List[SessionWithSpeaker])
def get_user_registered_sessions(
    current_user: User = Depends(get_current_active_user),
    session_service: SessionService = Depends(),
):
    """
    Get all sessions the current user is registered for
    """
    sessions = session_service.get_user_sessions(user_id=current_user.id)
    return sessions