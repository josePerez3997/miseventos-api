from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.speaker import Speaker
from app.schemas.speaker import SpeakerCreate, SpeakerUpdate
from app.repositories.base import BaseRepository

class SpeakerRepository(BaseRepository[Speaker, SpeakerCreate, SpeakerUpdate]):
    """
    Repository for Speaker model
    """
    def get_by_name(self, db: Session, *, name: str) -> List[Speaker]:
        """
        Get speakers by name (partial match)
        """
        return db.query(Speaker).filter(Speaker.name.ilike(f"%{name}%")).all()


speaker_repository = SpeakerRepository(Speaker)