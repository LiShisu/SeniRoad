from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ELDERLY = "elderly"
    FAMILY = "family"

class UserBase(BaseModel):
    phone: Optional[str] = Field(None, min_length=11, max_length=20)
    nickname: Optional[str] = None
    role: UserRole = Field(default=UserRole.ELDERLY)
    gender: Optional[int] = Field(None, ge=0, le=9)
    birthday: Optional[str] = None
    avatar_url: Optional[str] = None
    openid: str

class UserResponse(UserBase):
    user_id: int
    nickname: Optional[str] = None
    role: UserRole
    gender: Optional[int] = None
    birthday: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class WechatUserCreate(BaseModel):
    code: str
    nickname: str
    phone: str
    role: UserRole = Field(default=UserRole.ELDERLY)

class WechatLoginRequest(BaseModel):
    code: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    gender: Optional[int] = Field(None, ge=0, le=9)
    birthday: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
