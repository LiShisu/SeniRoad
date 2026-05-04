from pydantic import BaseModel
from typing import Optional, List

class NavigationPlanRequest(BaseModel):
    favorite_place_id: int
    origin_lng: str
    origin_lat: str

class NavigationStep(BaseModel):
    instruction: str
    distance: str
    duration: str
    road: Optional[str] = ""
    polyline: str

class NavigationRoute(BaseModel):
    record_id: int
    origin: str
    destination: str
    distance: str
    duration: str
    steps: List[NavigationStep]
    polyline: str

class NavigationPlanResponse(BaseModel):
    status: str
    destination: str
    place_name: Optional[str] = None
    route: NavigationRoute
    latitude: str
    longitude: str
