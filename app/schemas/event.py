from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class EventStatus(str, Enum):
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class EventBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=20)
    location: str = Field(..., min_length=5, max_length=200)
    date: datetime
    end_date: Optional[datetime] = None
    capacity: int = Field(..., gt=0, le=10000)
    status: EventStatus = EventStatus.UPCOMING
    image_url: Optional[str] = None
    category_ids: Optional[List[int]] = []

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
    category_ids: Optional[List[int]] = None

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if v and 'date' in values and values['date'] and v < values['date']:
            raise ValueError('end_date must be after start date')
        return v

class CategorySummary(BaseModel):
    id: int
    name: str
    color: Optional[str] = None

    class Config:
        from_attributes = True

class Event(EventBase):
    id: int
    registered_attendees: int
    organizer_id: int
    created_at: datetime
    updated_at: datetime
    categories: List[CategorySummary] = []

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
    location: Optional[str] = None
    organizer_id: Optional[int] = None
    category_id: Optional[int] = None  # Filter by category ID
    category_ids: Optional[List[int]] = None  # Filter by multiple category IDs
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_capacity: Optional[int] = None
    max_capacity: Optional[int] = None
    has_available_spots: Optional[bool] = None
    sort_by: Optional[str] = "date"  # Options: date, name, popularity
    sort_order: Optional[str] = "asc"  # Options: asc, desc
    page: int = 1
    size: int = 10

    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_sort_fields = ['date', 'name', 'popularity', 'capacity']
        if v and v not in allowed_sort_fields:
            raise ValueError(f'sort_by must be one of {allowed_sort_fields}')
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v and v not in ['asc', 'desc']:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v