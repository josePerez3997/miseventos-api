from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, max_length=20)

    @validator('color')
    def validate_color(cls, v):
        """Validar que el color tenga un formato válido (hexadecimal o nombre de color CSS)"""
        if v is not None:
            import re
            if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', v) and not re.match(r'^[a-zA-Z]+$', v):
                raise ValueError('color must be a valid hex code (#RRGGBB) or CSS color name')
        return v

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, max_length=20)

    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            import re
            if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', v) and not re.match(r'^[a-zA-Z]+$', v):
                raise ValueError('color must be a valid hex code (#RRGGBB) or CSS color name')
        return v

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryWithEvents(Category):
    events: List[dict] = []