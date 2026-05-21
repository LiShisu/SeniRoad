from httpx import AsyncClient
from app.config import settings
# from app.agent.destination_parse_agent import DestinationParseAgent
# from app.agent.multi_agent_navigation import MultiAgentNavigation
# 延迟导入以避免循环导入
# from app.agent.workflow import execute_navigation_workflow, execute_navigation_workflow_stream
from app.services.voice_log import VoiceLogService
from app.services.navigation_record import NavigationRecordService
from app.schemas.voice_log import VoiceLogCreate
from app.schemas.navigation_record import NavigationRecordCreate
from app.schemas.exception import BusinessException, NotFoundException
from app.services.favorite_place import FavoritePlaceService
from fastapi import UploadFile
from typing import Dict, List, Optional, AsyncGenerator, Any
from datetime import datetime
from decimal import Decimal
import logging
import asyncio
import json
import httpx
import re
from app.schemas.navigation import (
    NavigationPlanResponse,
    SmartNavigationResponse,
    VoiceNavigationResponse,
    NavigationRoute,
    SmartNavigationRoute
)

logger = logging.getLogger(__name__)

class NavigationService:
    def __init__(
        self,
        navigation_record_service: NavigationRecordService,
        voice_log_service: VoiceLogService,
        favorite_place_service: FavoritePlaceService,
        # destination_parse_agent: Optional[DestinationParseAgent] = None,
        # multi_agent_navigation: Optional[MultiAgentNavigation] = None,
    ):
        self.client = AsyncClient()
        self.amap_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
        # self.destination_parse_agent = destination_parse_agent
        # self.multi_agent_navigation = multi_agent_navigation
        self.navigation_record_service = navigation_record_service
        self.voice_log_service = voice_log_service
        self.favorite_place_service = favorite_place_service

    # async def _stream_navigation_events(
    #     self,
    #     origin: str,
    #     destination: str,
    # ) -> AsyncGenerator[Dict[str, Any], None]:
    #     async for event in self.multi_agent_navigation.plan_travel_stream(origin, destination):
    #         yield event

    def _format_sse_event(self, event_type: str, data: Any) -> str:
        return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    async def plan(
        self,
        origin_lng: str,
        origin_lat: str,
        favorite_place_id: int,
        user_id: int,
    ) -> NavigationPlanResponse:  # 【规范】严格返回强类型 DTO
        favorite_place = self.favorite_place_service.get_place_by_id(favorite_place_id)
        if not favorite_place:
            raise NotFoundException("收藏地点不存在")

        dest_lat = str(favorite_place.latitude)
        dest_lng = str(favorite_place.longitude)
        origin = f"{origin_lng},{origin_lat}"
        destination = f"{dest_lng},{dest_lat}"

        params = {
            "origin": origin,
            "destination": destination,
            "key": self.amap_key,
            "extensions": "all"
        }

        response = await self.client.get(f"{self.base_url}/direction/walking", params=params)
        result = response.json()

        if result.get("status") != "1":
            raise BusinessException(code=400, message=f"导航规划失败: {result.get('info', '未知错误')}")

        route = result.get("route", {})
        paths = route.get("paths", [])

        if not paths:
            raise BusinessException(code=404, message="未找到可行的导航路线")

        path = paths[0]
        steps = []
        for step in path.get("steps", []):
            road = step.get("road", "")
            if isinstance(road, list):
                road = ""
            steps.append({
                "instruction": step.get("instruction", ""),
                "distance": step.get("distance", ""),
                "duration": step.get("duration", ""),
                "road": road,
                "polyline": step.get("polyline", "")
            })

        polyline = ";".join([step.get("polyline", "") for step in steps])

        record_data = NavigationRecordCreate(
            user_id=user_id,
            start_time=datetime.now(),
            origin_lat=Decimal(origin_lat),
            origin_lng=Decimal(origin_lng),
            dest_lat=favorite_place.latitude,
            dest_lng=favorite_place.longitude,
            dest_name=favorite_place.address,
            polyline=polyline,
            status=1
        )
        record = self.navigation_record_service.create_record(record_data)
        return NavigationPlanResponse(
            status="success",
            destination=favorite_place.address,
            place_name=favorite_place.place_name,
            route=NavigationRoute(
                record_id=record.record_id,
                origin=route.get("origin", origin),
                destination=route.get("destination", destination),
                distance=path.get("distance", ""),
                duration=path.get("duration", ""),
                steps=steps,
                polyline=polyline
            ),
            latitude=dest_lat,
            longitude=dest_lng
        )

    async def get_fast_amap_route(
        self,
        origin_lng: str,
        origin_lat: str,
        dest_lng: str,
        dest_lat: str
    ) -> NavigationRoute:
        origin = f"{origin_lng},{origin_lat}"
        destination = f"{dest_lng},{dest_lat}"

        params = {
            "origin": origin,
            "destination": destination,
            "key": self.amap_key,
            "extensions": "all"
        }

        response = await self.client.get(f"{self.base_url}/direction/walking", params=params)
        result = response.json()

        if result.get("status") != "1":
            raise BusinessException(code=400, message=f"高德偏航重算失败: {result.get('info', '未知错误')}")

        route = result.get("route", {})
        paths = route.get("paths", [])

        if not paths:
            raise BusinessException(code=404, message="未找到可行的重算路线")

        path = paths[0]
        steps = []

        for step in path.get("steps", []):
            road = step.get("road", "")
            if isinstance(road, list):
                road = ""
                
            steps.append({
                "instruction": step.get("instruction", ""),
                "distance": step.get("distance", ""),
                "duration": step.get("duration", ""),
                "road": road,
                "polyline": step.get("polyline", "")
            })

        polyline = ";".join([step.get("polyline", "") for step in steps])

        return NavigationRoute(
            origin=route.get("origin", origin),
            destination=route.get("destination", destination),
            distance=path.get("distance", ""),
            duration=path.get("duration", ""),
            polyline=polyline,
            steps=steps
        )
    
    async def process_text_navigation(
        self,
        origin_lng: str,
        origin_lat: str,
        favorite_place_id: int,
        user_id: int,
    ) -> SmartNavigationResponse:  # 【规范】严格返回强类型 DTO
        # 延迟导入避免循环导入
        from app.agent.workflow import execute_navigation_workflow
        
        favorite_place = self.favorite_place_service.get_place_by_id(favorite_place_id)
        if not favorite_place:
            raise NotFoundException("收藏地点不存在")

        destination = favorite_place.address
        latitude = favorite_place.latitude
        longitude = favorite_place.longitude

        logger.info(f"开始导航，起点：经度{origin_lng},纬度{origin_lat}，终点：{destination}")

        # 使用新的工作流
        navigation_result = await execute_navigation_workflow(
            origin_lng=origin_lng,
            origin_lat=origin_lat,
            user_id=user_id,
            destination_name=destination,
            destination_lng=str(longitude) if longitude else None,
            destination_lat=str(latitude) if latitude else None,
            favorite_place_id=favorite_place_id,
            favorite_place_service=self.favorite_place_service
        )

        route_data = navigation_result.get("route", {})
        weather_data = navigation_result.get("weather", {})
        advice_data = navigation_result.get("advice", "")

        # 创建导航记录
        record_data = NavigationRecordCreate(
            user_id=user_id,
            start_time=datetime.now(),
            origin_lat=Decimal(origin_lat),
            origin_lng=Decimal(origin_lng),
            dest_lat=Decimal(latitude) if latitude else None,
            dest_lng=Decimal(longitude) if longitude else None,
            dest_name=favorite_place.address,
            polyline=route_data.get("polyline", ""),
            status=1
        )
        record = self.navigation_record_service.create_record(record_data)
        
        return SmartNavigationResponse(
            status="success",
            destination=destination,
            place_name=favorite_place.place_name,
            navigation_advice=advice_data,
            route=SmartNavigationRoute(
                record_id=record.record_id,
                text=route_data.get("text", ""),
                origin=f"{origin_lng},{origin_lat}",
                destination=f"{longitude},{latitude}" if longitude and latitude else "",
                distance=str(route_data.get("distance", "")),
                duration=str(route_data.get("duration", "")),
                steps=route_data.get("steps", []),
                polyline=route_data.get("polyline", "")
            ),
            weather=weather_data,
            latitude=float(latitude) if latitude else 0.0,
            longitude=float(longitude) if longitude else 0.0
        )

    async def process_text_navigation_stream(
        self,
        origin_lng: str,
        origin_lat: str,
        favorite_place_id: int,
        user_id: int,
        travel_mode: str = "walking", # 👈 补充参数
        city: str = ""
    ) -> AsyncGenerator[str, None]:
        # 延迟导入避免循环导入
        from app.agent.workflow import execute_navigation_workflow_stream
        
        try:
            yield self._format_sse_event("start", {"status": "开始处理导航请求..."})

            favorite_place = self.favorite_place_service.get_place_by_id(favorite_place_id)
            if not favorite_place:
                yield self._format_sse_event("error", {"error": "收藏地点不存在"})
                return

            destination = favorite_place.address
            latitude = favorite_place.latitude
            longitude = favorite_place.longitude

            yield self._format_sse_event("destination", {
                "destination": destination, 
                "place_name": favorite_place.place_name
            })

            route_data = {}
            async for event in execute_navigation_workflow_stream(
                origin_lng=origin_lng,
                origin_lat=origin_lat,
                user_id=user_id,
                destination_name=destination,
                destination_lng=str(longitude) if longitude else None,
                destination_lat=str(latitude) if latitude else None,
                favorite_place_id=favorite_place_id,
                favorite_place_service=self.favorite_place_service,
                travel_mode=travel_mode, # 👈 传递下去
                city=city
            ):
                if event["event"] == "route":
                    route_data = event["data"]
                    logger.info(f"Received route data: {route_data}")
                    yield self._format_sse_event("route", route_data)
                elif event["event"] == "weather":
                    weather_data = event["data"]
                    logger.info(f"Received weather data: {weather_data}")
                    yield self._format_sse_event("weather", weather_data)
                elif event["event"] == "advice":
                    advice_data = event["data"]
                    yield self._format_sse_event("advice", advice_data)
                elif event["event"] == "complete":
                    # 创建导航记录
                    if route_data:
                        record_data = NavigationRecordCreate(
                            user_id=user_id,
                            start_time=datetime.now(),
                            origin_lat=Decimal(origin_lat),
                            origin_lng=Decimal(origin_lng),
                            dest_lat=Decimal(latitude) if latitude else None,
                            dest_lng=Decimal(longitude) if longitude else None,
                            dest_name=favorite_place.address,
                            polyline=route_data.get("polyline", ""),
                            status=1
                        )
                        self.navigation_record_service.create_record(record_data)
                    yield self._format_sse_event("complete", {"status": "done"})

        except Exception as e:
            yield self._format_sse_event("error", {"error": str(e)})

    async def process_voice_navigation(
        self,
        audio_file: UploadFile,
        user_id: int,
        origin_lng: str,
        origin_lat: str
    ) -> VoiceNavigationResponse:  # 【规范】严格返回强类型 DTO
        # 延迟导入避免循环导入
        from app.agent.workflow import execute_navigation_workflow

        # 使用新的工作流
        navigation_result = await execute_navigation_workflow(
            origin_lng=origin_lng,
            origin_lat=origin_lat,
            user_id=user_id,
            audio_file=audio_file,
            favorite_place_service=self.favorite_place_service
        )

        voice_text = navigation_result.get("voice_text", "")
        destination = navigation_result.get("destination_name", "")
        matched_type = navigation_result.get("matched_type", "")
        latitude = navigation_result.get("destination_lat")
        longitude = navigation_result.get("destination_lng")

        if not destination:
            raise BusinessException(code=400, message="无法从语音中解析出目的地，请再说一遍")

        route_data = navigation_result.get("route", {})
        weather_data = navigation_result.get("weather", "")
        advice_data = navigation_result.get("advice", "")

        # 创建导航记录
        record_id = None
        if latitude and longitude:
            record_data = NavigationRecordCreate(
                user_id=user_id,
                start_time=datetime.now(),
                origin_lat=Decimal(origin_lat),
                origin_lng=Decimal(origin_lng),
                dest_lat=Decimal(latitude),
                dest_lng=Decimal(longitude),
                dest_name=destination,
                polyline=route_data.get("polyline", ""),
                status=1
            )
            record = self.navigation_record_service.create_record(record_data)
            record_id = record.record_id
        
        voice_log = VoiceLogCreate(
            user_id=user_id,
            audio_url=audio_file.filename,
            record_id=record_id,
            asr_text=voice_text,
            intent_json={
                "destination": destination,
                "matched_type": matched_type,
                "origin": f"{origin_lng},{origin_lat}"
            },
            response_text=advice_data,
            log_time=datetime.now()
        )
        self.voice_log_service.create_log(voice_log)
        
        # 清理 route.origin 和 route.destination，去除"经度""纬度"字样
        route_origin = route_data.get("origin", "")
        route_destination = route_data.get("destination", "")
        
        # 使用正则表达式提取经纬度数值
        origin_match = re.search(r'经度([0-9.]+)[,，]纬度([0-9.]+)', route_origin)
        if origin_match:
            route_origin = f"{origin_match.group(1)},{origin_match.group(2)}"
        
        dest_match = re.search(r'经度([0-9.]+)[,，]纬度([0-9.]+)', route_destination)
        if dest_match:
            route_destination = f"{dest_match.group(1)},{dest_match.group(2)}"

        return VoiceNavigationResponse(
            status="success",
            voice_text=voice_text,
            destination=destination,
            matched_type=matched_type,
            navigation_advice=advice_data,
            route=SmartNavigationRoute(
                record_id=record_id,
                text=route_data.get("text", ""),
                origin=route_origin,
                destination=route_destination,
                distance=str(route_data.get("distance", "")),
                duration=str(route_data.get("duration", "")),
                steps=route_data.get("steps", []),
                polyline=route_data.get("polyline", "")
            ),
            weather=weather_data,
            latitude=float(latitude) if latitude else 0.0,
            longitude=float(longitude) if longitude else 0.0
        )

    async def process_voice_navigation_stream(
        self,
        audio_file: UploadFile,
        user_id: int,
        origin_lng: str,
        origin_lat: str,
        travel_mode: str = "walking", # 🌟 锁住多模态
        city: str = ""                # 🌟 锁住城市
    ) -> AsyncGenerator[str, None]:
        # 延迟导入避免循环导入
        from app.agent.workflow import execute_navigation_workflow_stream
        
        try:
            yield self._format_sse_event("start", {"status": "开始处理语音导航请求..."})

            route_data = {}
            destination = ""
            voice_text = ""
            matched_type = ""
            
            # 🌟 防御性变量：提前初始化，防止在 destination 事件外拿不到坐标
            latitude = None
            longitude = None

            async for event in execute_navigation_workflow_stream(
                origin_lng=origin_lng,
                origin_lat=origin_lat,
                user_id=user_id,
                audio_file=audio_file,
                favorite_place_service=self.favorite_place_service,
                travel_mode=travel_mode, # 🌟 核心修改 3：深层灌入大模型状态机
                city=city                # 🌟 核心修改 3：深层灌入大模型状态机
            ):
                if event["event"] == "destination":
                    destination = event["data"]["destination"]
                    matched_type = event["data"]["matched_type"]
                    voice_text = event["data"]["voice_text"]
                    
                    # 🌟 核心修复：直接从解析结果中拦截并锁死终点经纬度，最安全、最通配！
                    latitude = event["data"].get("destination_lat")
                    longitude = event["data"].get("destination_lng")
                    
                    yield self._format_sse_event("destination", event["data"])
                    
                elif event["event"] == "route":
                    route_data = event["data"]
                    yield self._format_sse_event("route", route_data)
                    
                elif event["event"] == "weather":
                    weather_data = event["data"]
                    yield self._format_sse_event("weather", weather_data)
                    
                elif event["event"] == "advice":
                    advice = event["data"]
                    yield self._format_sse_event("advice", advice)
                    
                    # 3. 创建导航记录与日志
                    current_record_id = None
                    # 此时 latitude 和 longitude 百分百有值，哪怕是公交模式也不会出错
                    if latitude and longitude:
                        record_data = NavigationRecordCreate(
                            user_id=user_id,
                            start_time=datetime.now(),
                            origin_lat=Decimal(origin_lat),
                            origin_lng=Decimal(origin_lng),
                            dest_lat=Decimal(str(latitude)),
                            dest_lng=Decimal(str(longitude)),
                            dest_name=destination,
                            polyline=route_data.get("polyline", ""),
                            status=1
                        )
                        saved_record = self.navigation_record_service.create_record(record_data)
                        current_record_id = getattr(saved_record, "record_id", getattr(saved_record, "id", None))
                    
                    voice_log = VoiceLogCreate(
                        user_id=user_id,
                        audio_url=audio_file.filename,
                        asr_text=voice_text,
                        intent_json={
                            "destination": destination,
                            "matched_type": matched_type,
                            "origin": f"{origin_lng},{origin_lat}",
                            "travel_mode": travel_mode # 顺手存入日志，方便后续大数据统计长辈出行习惯
                        },
                        response_text=json.dumps(advice, ensure_ascii=False),
                        log_time=datetime.now(),
                        record_id=current_record_id
                    )
                    self.voice_log_service.create_log(voice_log)
                    
                elif event["event"] == "complete":
                    yield self._format_sse_event("complete", {"status": "done"})

        except Exception as e:
            yield self._format_sse_event("error", {"error": str(e)})
