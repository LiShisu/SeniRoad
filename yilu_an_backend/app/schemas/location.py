from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class LocationBase(BaseModel):
    latitude: Decimal = Field(..., ge=-90, le=90, description="纬度")
    longitude: Decimal = Field(..., ge=-180, le=180, description="经度")
    address: Optional[str] = Field(None, max_length=255, description="地址")
    accuracy: Optional[float] = Field(None, ge=0, description="精度（米）")
    record_id: Optional[int] = Field(None, description="关联的导航记录ID")

class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    pass

class LocationResponse(LocationBase):
    location_id: int
    user_id: int
    record_id: Optional[int] = Field(None, description="关联的导航记录ID")
    latitude: Decimal
    longitude: Decimal
    address: Optional[str] = Field(None, max_length=255, description="地址")
    accuracy: Optional[float] = Field(None, ge=0, description="精度（米）")
    created_at: datetime

    class Config:
        from_attributes = True
