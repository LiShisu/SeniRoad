from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LocationBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    accuracy: Optional[float] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
