from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TagBase(BaseModel):
    tag_name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=7, description="标签颜色，十六进制，如 #FF5733")
    icon: Optional[str] = Field(None, max_length=50, description="标签图标名称")
    is_active: bool = Field(True, description="是否启用")

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    tag_name: Optional[str] = Field(None, min_length=1, max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=7, description="标签颜色")
    icon: Optional[str] = Field(None, max_length=50, description="标签图标名称")
    is_active: Optional[bool] = Field(None, description="是否启用")

class TagResponse(TagBase):
    tag_id: int
    created_at: datetime

    class Config:
        from_attributes = True
