from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class BindingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

# 1. 新增：子资源表述，专门用于在绑定关系中展示用户信息
class BindingUser(BaseModel):
    user_id: int
    phone: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
# 【新增】：告诉 Pydantic 允许从 SQLAlchemy 的 User 对象读取属性
    model_config = ConfigDict(from_attributes=True)
# 2. 读表述：使用嵌套结构，清晰反映实体关系
class BindingResponse(BaseModel):
    binding_id: int
    status: BindingStatus
    created_at: datetime
    approved_at: Optional[datetime] = None
    # 嵌套结构，拒绝平铺数据库字段
    elderly: Optional[BindingUser] = None
    family: Optional[BindingUser] = None
    model_config = ConfigDict(from_attributes=True)
# class BindingCreate(BaseModel):
#     elderly_phone: str
#     family_id: Optional[int] = None

# 3. 写表述：发起绑定只需要老人手机号。family_id 绝对不能由前端传入
class BindingCreate(BaseModel):
    elderly_phone: str = Field(..., description="要绑定的老人手机号")

# 4. 写表述：状态更新（替代原来的 /approve 和 /reject）
class BindingStatusUpdate(BaseModel):
    status: BindingStatus = Field(..., description="目标状态：accepted 或 rejected")
# class BindingResponse(BaseModel):
#     binding_id: int
#     elderly_id: int
#     family_id: int
#     elderly_nickname: Optional[str] = None
#     elderly_phone: Optional[str] = None
#     family_nickname: Optional[str] = None
#     family_phone: Optional[str] = None
#     status: BindingStatus
#     created_at: datetime
#     approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BindingUnbind(BaseModel):
    elderly_phone: str
    family_id: Optional[int] = None

