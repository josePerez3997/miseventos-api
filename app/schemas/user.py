from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True
    is_superuser: bool = False
    role: int = 3
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role: Optional[int] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class CurrentUser(User):
    pass