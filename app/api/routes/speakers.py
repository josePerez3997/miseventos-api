from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_active_user, get_current_active_superuser
from app.models.user import User
from app.services.speaker_service import SpeakerService
from app.schemas.speaker import Speaker, SpeakerCreate, SpeakerUpdate

router = APIRouter()

@router.get("", response_model=List[Speaker])
def get_speakers(
    name: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    speaker_service: SpeakerService = Depends(),
):
    """
    Get all speakers with optional name filter
    """
    if name:
        speakers = speaker_service.search_speakers(name=name)
    else:
        speakers = speaker_service.get_speakers(skip=skip, limit=limit)
    
    return speakers

@router.post("", response_model=Speaker, status_code=status.HTTP_201_CREATED)
def create_speaker(
    speaker_in: SpeakerCreate,
    current_user: User = Depends(get_current_active_user),
    speaker_service: SpeakerService = Depends(),
):
    """
    Create a new speaker (any authenticated user)
    """
    speaker = speaker_service.create_speaker(speaker_in=speaker_in)
    return speaker

@router.get("/{speaker_id}", response_model=Speaker)
def get_speaker(
    speaker_id: int,
    speaker_service: SpeakerService = Depends(),
):
    """
    Get a specific speaker by ID
    """
    speaker = speaker_service.get_speaker(speaker_id=speaker_id)
    if not speaker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaker not found",
        )
    return speaker

@router.put("/{speaker_id}", response_model=Speaker)
def update_speaker(
    speaker_id: int,
    speaker_in: SpeakerUpdate,
    current_user: User = Depends(get_current_active_user),
    speaker_service: SpeakerService = Depends(),
):
    """
    Update a speaker (any authenticated user)
    """
    speaker = speaker_service.update_speaker(
        speaker_id=speaker_id, 
        speaker_in=speaker_in
    )
    if not speaker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaker not found",
        )
    return speaker

@router.delete("/{speaker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_speaker(
    speaker_id: int,
    current_user: User = Depends(get_current_active_superuser),
    speaker_service: SpeakerService = Depends(),
):
    """
    Delete a speaker if not used in any session (admin only)
    """
    success = speaker_service.delete_speaker(speaker_id=speaker_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete speaker because it is used in one or more sessions",
        )
    return None