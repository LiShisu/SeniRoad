from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DeviceBase(BaseModel):
    user_id: int = Field(..., description="关联的用户ID(老人)")
    device_token: str = Field(..., min_length=1, max_length=255, description="设备唯一标识/Token")
    device_model: Optional[str] = Field(None, max_length=100, description="设备型号")
    status: int = Field(1, ge=0, le=1, description="状态: 1-在线, 0-离线")

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    device_model: Optional[str] = Field(None, max_length=100, description="设备型号")
    last_login_time: Optional[datetime] = Field(None, description="最后登录时间")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态: 1-在线, 0-离线")

class DeviceResponse(DeviceBase):
    device_id: int
    last_login_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
