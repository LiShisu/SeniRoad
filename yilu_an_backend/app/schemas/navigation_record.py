from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class NavigationRecordBase(BaseModel):
    user_id: int = Field(..., description="用户ID")
    start_time: datetime = Field(..., description="导航开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    origin_lat: Optional[Decimal] = Field(None, ge=-90, le=90, description="起点纬度")
    origin_lng: Optional[Decimal] = Field(None, ge=-180, le=180, description="起点经度")
    dest_lat: Decimal = Field(..., ge=-90, le=90, description="终点纬度")
    dest_lng: Decimal = Field(..., ge=-180, le=180, description="终点经度")
    dest_name: Optional[str] = Field(None, max_length=100, description="目的地名称")
    status: int = Field(1, ge=1, le=3, description="状态: 1-进行中, 2-完成, 3-取消")

class NavigationRecordCreate(NavigationRecordBase):
    pass

class NavigationRecordUpdate(BaseModel):
    end_time: Optional[datetime] = Field(None, description="结束时间")
    origin_lat: Optional[Decimal] = Field(None, ge=-90, le=90, description="起点纬度")
    origin_lng: Optional[Decimal] = Field(None, ge=-180, le=180, description="起点经度")
    dest_name: Optional[str] = Field(None, max_length=100, description="目的地名称")
    status: Optional[int] = Field(None, ge=1, le=3, description="状态")

class NavigationRecordResponse(NavigationRecordBase):
    record_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
