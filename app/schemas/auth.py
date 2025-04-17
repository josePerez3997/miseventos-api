from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None 

class Login(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class Register(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    
class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)