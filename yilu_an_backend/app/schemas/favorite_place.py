from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class FavoritePlaceBase(BaseModel):
    user_id: int = Field(..., description="所属老人ID")
    place_name: str = Field(..., min_length=1, max_length=100, description="地点名称(如: 儿子家)")
    latitude: Decimal = Field(..., ge=-90, le=90, description="纬度")
    longitude: Decimal = Field(..., ge=-180, le=180, description="经度")
    address: str = Field(..., min_length=1, max_length=500, description="详细地址")
    source_type: int = Field(1, ge=1, le=2, description="来源: 1-家属预设, 2-自动识别")
    is_active: int = Field(1, ge=0, le=1, description="是否激活")

class FavoritePlaceCreate(FavoritePlaceBase):
    pass

class FavoritePlaceUpdate(BaseModel):
    place_name: Optional[str] = Field(None, min_length=1, max_length=100, description="地点名称")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="纬度")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="经度")
    address: Optional[str] = Field(None, min_length=1, max_length=500, description="详细地址")
    source_type: Optional[int] = Field(None, ge=1, le=2, description="来源")
    is_active: Optional[int] = Field(None, ge=0, le=1, description="是否激活")

class FavoritePlaceResponse(FavoritePlaceBase):
    place_id: int
    
    class Config:
        from_attributes = True
