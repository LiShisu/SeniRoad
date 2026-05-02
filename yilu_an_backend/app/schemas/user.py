from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime, date
from enum import Enum

from app.models.user import UserRole

class UserBase(BaseModel):
    phone: Optional[str] = Field(None, min_length=11, max_length=20)
    nickname: Optional[str] = None
    role: UserRole = Field(default=UserRole.ELDERLY)
    gender: Optional[int] = Field(None, ge=0, le=9)
    birthday: Optional[date] = None
    avatar_url: Optional[str] = None
    openid: str

class UserResponse(UserBase):
    user_id: int
    nickname: Optional[str] = None
    role: UserRole
    gender: Optional[int] = None
    birthday: Optional[date] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime

    @field_serializer("birthday")
    @classmethod
    def serialize_birthday(cls, v: Optional[date]) -> Optional[str]:
        return v.isoformat() if v is not None else None

    class Config:
        from_attributes = True

class WechatUserCreate(BaseModel):
    code: str
    nickname: str
    phone: str
    role: UserRole = Field(default=UserRole.ELDERLY)

class WechatLoginRequest(BaseModel):
    code: str
    role: UserRole = Field(default=UserRole.ELDERLY)

class PhoneLoginRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    gender: Optional[int] = Field(None, ge=0, le=9)
    birthday: Optional[date] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
