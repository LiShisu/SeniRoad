from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DestinationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_common: bool = False

class DestinationCreate(DestinationBase):
    pass

class DestinationResponse(DestinationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
