from typing import List, Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies.db import get_database
from app.repositories.speaker_repository import speaker_repository
from app.models.speaker import Speaker
from app.schemas.speaker import SpeakerCreate, SpeakerUpdate

class SpeakerService:
    """
    Service for speaker related operations
    """
    def __init__(self, db: Session = Depends(get_database)):
        self.db = db
    
    def get_speaker(self, speaker_id: int) -> Optional[Speaker]:
        """
        Get a speaker by ID
        """
        return speaker_repository.get(self.db, id=speaker_id)
    
    def get_speakers(self, skip: int = 0, limit: int = 100) -> List[Speaker]:
        """
        Get a list of speakers
        """
        return speaker_repository.get_multi(self.db, skip=skip, limit=limit)
    
    def create_speaker(self, speaker_in: SpeakerCreate) -> Speaker:
        """
        Create a new speaker
        """
        return speaker_repository.create(self.db, obj_in=speaker_in)
    
    def update_speaker(self, speaker_id: int, speaker_in: SpeakerUpdate) -> Optional[Speaker]:
        """
        Update a speaker
        """
        speaker = self.get_speaker(speaker_id)
        if not speaker:
            return None
        
        return speaker_repository.update(self.db, db_obj=speaker, obj_in=speaker_in)
    
    def delete_speaker(self, speaker_id: int) -> bool:
        """
        Delete a speaker if not used in any session
        """
        speaker = self.get_speaker(speaker_id)
        if not speaker:
            return False
        
        if speaker.sessions:
            return False
        
        speaker_repository.remove(self.db, id=speaker_id)
        return True
    
    def search_speakers(self, name: str) -> List[Speaker]:
        """
        Search speakers by name
        """
        return speaker_repository.get_by_name(self.db, name=name)