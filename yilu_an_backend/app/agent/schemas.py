"""
智能导航工作流状态定义

定义LangGraph工作流中使用的状态类和模式。
使用 Pydantic BaseModel 进行数据验证和序列化。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Sequence
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import Union
#TODO：待移动到schemas文件夹
class WeatherResult(BaseModel):
    """天气查询结果结构
    
    与 multi_agent_navigation.py 中的天气Agent返回格式保持一致
    """
    weather_text: str = Field(default="", description="天气现象的描述（如：晴、多云、小雨）")
    temperature: str = Field(default="", description="当前温度（如：25℃）")
    wind: str = Field(default="", description="风力情况（如：3-4级北风）")
    humidity: str = Field(default="", description="湿度（如：60%）")


class RouteStep(BaseModel):
    """路线步骤结构"""
    instruction: str = Field(default="", description="转向指示")
    distance: str = Field(default="", description="该步距离（米）")
    duration: str = Field(default="", description="该步时间（秒）")
    road: str = Field(default="", description="道路名称")
    polyline: str = Field(default="", description="路线坐标点")


class RouteResult(BaseModel):
    """路线规划结果结构
    
    与 multi_agent_navigation.py 中的路线Agent返回格式保持一致
    """
    text: str = Field(default="", description="路线文本描述")
    origin: str = Field(default="", description="出发地描述")
    destination: str = Field(default="", description="目的地描述")
    distance: str = Field(default="", description="总距离（米）")
    duration: str = Field(default="", description="总时间（秒）")
    steps: List[RouteStep] = Field(default_factory=list, description="路线步骤数组")
    polyline: str = Field(default="", description="路线坐标点，用;分隔的经纬度对")


class AdviceResult(BaseModel):
    """出行建议结果结构
    
    与 multi_agent_navigation.py 中的顾问Agent返回格式保持一致
    """
    clothing_advice: str = Field(default="", description="穿衣建议")
    items_to_bring: List[str] = Field(default_factory=list, description="需要携带的物品数组")
    safety_reminders: List[str] = Field(default_factory=list, description="安全提醒数组")
    best_time: str = Field(default="", description="最佳出行时段建议")
    tips: List[str] = Field(default_factory=list, description="其他贴心小贴士数组")


class NavigationWorkflowState(BaseModel):
    """导航工作流状态类

    包含导航过程中需要传递的所有状态信息：
    - messages: 对话历史
    - user_id: 用户ID
    - origin_lng: 起点经度
    - origin_lat: 起点纬度
    - destination_name: 目的地名称
    - destination_lng: 目的地经度
    - destination_lat: 目的地纬度
    - favorite_place_id: 收藏地点ID（可选）
    - audio_file: 音频文件（语音导航时提供）
    - route_result: 路线规划结果
    - weather_result: 天气查询结果
    - final_advice: 最终出行建议
    - matched_type: 目的地匹配类型（llm/favorite/amap）
    - voice_text: 语音识别文本
    """
    messages: Sequence[BaseMessage] = Field(default_factory=list, description="对话历史")
    user_id: Optional[int] = Field(default=None, description="用户ID")
    origin_lng: str = Field(default="", description="起点经度")
    origin_lat: str = Field(default="", description="起点纬度")
    destination_name: str = Field(default="", description="目的地名称")
    destination_lng: Optional[str] = Field(default=None, description="目的地经度")
    destination_lat: Optional[str] = Field(default=None, description="目的地纬度")
    favorite_place_id: Optional[int] = Field(default=None, description="收藏地点ID")
    audio_file: Optional[Any] = Field(default=None, description="音频文件")
    route_result: Union[RouteResult, TransitRouteResult] = Field(default_factory=RouteResult, description="路线规划结果")
    weather_result: WeatherResult = Field(default_factory=WeatherResult, description="天气查询结果")
    final_advice: str = Field(default="", description="最终出行建议")
    matched_type: str = Field(default="", description="目的地匹配类型")
    voice_text: str = Field(default="", description="语音识别文本")
    travel_mode: str = Field(default="walking", description="出行方式（walking/transit）")
    city: Optional[str] = Field(default=None, description="城市名称或区号（公交规划必需）")

# --- 新增公交专属模型 ---
class TransitLine(BaseModel):
    name: str           # e.g., "地铁1号线"
    departure_stop: str # 上车站
    arrival_stop: str   # 下车站
    via_num: int        # 乘坐站数
    duration: str       # 乘车时间
    polyline: str       # 公交线路轨迹

class TransitSegment(BaseModel):
    walking: Optional[RouteStep] = None # 这一段的步行部分（前往车站）
    bus: Optional[TransitLine] = None   # 这一段的乘车部分

class TransitRouteResult(BaseModel):
    text: str
    distance: str
    duration: str
    segments: List[TransitSegment]      # 换乘段落
    polyline: str                       # 完整的总轨迹（前端画线用）