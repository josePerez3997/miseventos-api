from typing import Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class SpeakerBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    bio: str = Field(..., min_length=20)
    image_url: Optional[str] = None

class SpeakerCreate(SpeakerBase):
    pass

class SpeakerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    bio: Optional[str] = Field(None, min_length=20)
    image_url: Optional[str] = None

class Speaker(SpeakerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SpeakerWithSessions(Speaker):
    sessions: List[Any] = []