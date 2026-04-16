from pydantic import BaseModel, EmailStr, Field
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
    avatar_url: Optional[str] = None
    # 微信小程序相关字段
    openid: Optional[str] = None
"""
... (三个点) 是 Python 中 Ellipsis 的字面量，在这里作为 Field 的第一个参数（即默认值），
它有一个特殊的含义：表示这个字段是必填的。
创建数据模型实例时，必须为 字段 提供一个值，否则会引发验证错误。
"""

class UserResponse(UserBase):
    nickname: str
    role: UserRole
    avatar_url: Optional[str] = None
    phone: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True # 允许从 ORM 模型（如 SQLAlchemy 实例）直接转换为 Pydantic 模型

class WechatUserCreate(BaseModel):
    """微信小程序用户创建模型"""
    code: str
    nickname: str
    phone: str
    role: UserRole = Field(default=UserRole.ELDERLY)

class WechatLoginRequest(BaseModel):
    code: str

class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    role: UserRole

class UserUpdate(BaseModel):
    """用户更新模型"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
