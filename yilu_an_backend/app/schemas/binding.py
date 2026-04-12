from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class BindingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class BindingCreate(BaseModel):
    elderly_id: int
    family_id: int

class BindingResponse(BaseModel):
    id: int
    elderly_id: int
    family_id: int
    status: BindingStatus
    created_at: datetime
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BindingUnbind(BaseModel):
    elderly_id: int
    family_id: int
