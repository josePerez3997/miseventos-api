from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class EventStatus(str, Enum):
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# Esquema base para evento (campos comunes)
class EventBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=20)
    location: str = Field(..., min_length=5, max_length=200)
    date: datetime
    end_date: Optional[datetime] = None
    capacity: int = Field(..., gt=0, le=10000)
    status: EventStatus = EventStatus.UPCOMING
    image_url: Optional[str] = None

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if v and 'date' in values and v < values['date']:
            raise ValueError('end_date must be after start date')
        return v

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=20)
    location: Optional[str] = Field(None, min_length=5, max_length=200)
    date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    capacity: Optional[int] = Field(None, gt=0, le=10000)
    status: Optional[EventStatus] = None
    image_url: Optional[str] = None

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if v and 'date' in values and values['date'] and v < values['date']:
            raise ValueError('end_date must be after start date')
        return v

class Event(EventBase):
    id: int
    registered_attendees: int
    organizer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EventWithOrganizer(Event):
    organizer: Optional[Any] = None

class EventPage(BaseModel):
    items: List[Event]
    total: int
    page: int
    size: int
    pages: int

class EventSearchParams(BaseModel):
    search: Optional[str] = None
    status: Optional[EventStatus] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    size: int = 10