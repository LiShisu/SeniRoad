from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class BindingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class BindingCreate(BaseModel):
    elderly_phone: str
    family_id: Optional[int] = None

class BindingResponse(BaseModel):
    binding_id: int
    elderly_id: int
    family_id: int
    elderly_nickname: Optional[str] = None
    status: BindingStatus
    created_at: datetime
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BindingUnbind(BaseModel):
    elderly_phone: str
    family_id: Optional[int] = None
