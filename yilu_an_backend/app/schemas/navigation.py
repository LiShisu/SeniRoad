from pydantic import BaseModel
from typing import Optional, List
# ---------------- 请求表述 ----------------
class NavigationPlanRequest(BaseModel):
    favorite_place_id: int
    origin_lng: str
    origin_lat: str
    travel_mode: Optional[str] = "walking"  # 默认为步行
    city: Optional[str] = "济南市"


# ---------------- 子资源表述 ----------------
class NavigationStep(BaseModel):
    instruction: str
    distance: str
    duration: str
    road: Optional[str] = ""
    polyline: str

class NavigationRoute(BaseModel):
    record_id: Optional[int] = None
    origin: str
    destination: str
    distance: str
    duration: str
    steps: List[NavigationStep]
    polyline: str

class SmartNavigationRoute(NavigationRoute):
    text: Optional[str] = ""  # 大模型生成的路线文本描述

# 1. 基础地址导航响应
class NavigationPlanResponse(BaseModel):
    status: str
    destination: str
    place_name: Optional[str] = None
    route: NavigationRoute
    latitude: str
    longitude: str

# 2. 智能文本导航响应
class SmartNavigationResponse(BaseModel):
    status: str
    destination: str
    place_name: Optional[str] = None
    navigation_advice: str
    route: SmartNavigationRoute
    weather: str
    latitude: float
    longitude: float

# 3. 语音导航响应 (继承智能导航)
class VoiceNavigationResponse(SmartNavigationResponse):
    voice_text: str
    matched_type: str

class CoordinateNavRequest(BaseModel):
    origin_lng: str
    origin_lat: str
    dest_lng: str
    dest_lat: str