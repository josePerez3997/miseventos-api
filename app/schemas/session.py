from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

class SessionBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=20)
    speaker_id: int
    start_time: datetime
    end_time: datetime
    location: str = Field(..., min_length=3, max_length=100)
    capacity: int = Field(..., gt=0, le=1000)

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if v and 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class SessionCreate(SessionBase):
    event_id: int

class SessionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=20)
    speaker_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, min_length=3, max_length=100)
    capacity: Optional[int] = Field(None, gt=0, le=1000)

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class Session(SessionBase):
    id: int
    event_id: int
    registered_attendees: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SessionWithSpeaker(Session):
    speaker: Optional[Any] = None 

class SessionDetail(SessionWithSpeaker):
    event: Optional[Any] = None 