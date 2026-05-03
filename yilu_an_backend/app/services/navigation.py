from httpx import AsyncClient
from app.config import settings
from app.agent.destination_parse_agent import DestinationParseAgent
from app.agent.multi_agent_navigation import MultiAgentNavigation
from app.services.voice_log import VoiceLogService
from app.services.navigation_record import NavigationRecordService
from app.schemas.voice_log import VoiceLogCreate
from app.schemas.navigation_record import NavigationRecordCreate
from app.services.favorite_place import FavoritePlaceService
from fastapi import UploadFile
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

class NavigationService:
    def __init__(
        self,
        destination_parse_agent: Optional[DestinationParseAgent],
        multi_agent_navigation: Optional[MultiAgentNavigation],
        navigation_record_service: NavigationRecordService,
        voice_log_service: VoiceLogService,
        favorite_place_service: FavoritePlaceService,
    ):
        self.client = AsyncClient()
        self.amap_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
        self.destination_parse_agent = destination_parse_agent
        self.multi_agent_navigation = multi_agent_navigation
        self.navigation_record_service = navigation_record_service
        self.voice_log_service = voice_log_service
        self.favorite_place_service = favorite_place_service

    async def process_text_navigation(
        self,
        origin_lng: str,
        origin_lat: str,
        favorite_place_id: int,
        user_id: int,
    ) -> Dict:
            if not self.destination_parse_agent or not self.multi_agent_navigation:
                raise ValueError("服务未正确初始化，缺少必要的Agent组件")

            favorite_place = self.favorite_place_service.get_place_by_id(favorite_place_id)
            if not favorite_place:
                raise ValueError("收藏地点不存在")

            destination = favorite_place.address
            latitude = favorite_place.latitude
            longitude = favorite_place.longitude
            if latitude and longitude:
                destination = destination + f"，经度{longitude}，纬度{latitude}"

            origin = f"经度{origin_lng},纬度{origin_lat}"

            navigation_result = await self.multi_agent_navigation.plan_travel(origin, destination)

            route_data = navigation_result.get("route", {})
            weather_data = navigation_result.get("weather", "")
            advice_data = navigation_result.get("advice", "")

            # 创建导航记录
            record_data = NavigationRecordCreate(
                user_id=user_id,
                start_time=datetime.now(),
                origin_lat=Decimal(origin_lat),
                origin_lng=Decimal(origin_lng),
                dest_lat=Decimal(latitude),
                dest_lng=Decimal(longitude),
                dest_name=favorite_place.place_name,
                status=1
            )
            self.navigation_record_service.create_record(record_data)

            return {
                "status": "success",
                "destination": destination,
                "navigation_advice": advice_data,
                "route": {
                    "text": route_data.get("text", ""),
                    "origin": route_data.get("origin", origin),
                    "destination": route_data.get("destination", destination),
                    "distance": route_data.get("distance", ""),
                    "duration": route_data.get("duration", ""),
                    "steps": route_data.get("steps", []),
                    "polyline": route_data.get("polyline", "")
                },
                "weather": weather_data,
                "latitude": latitude,
                "longitude": longitude
            }


    async def process_voice_navigation(
        self,
        audio_file: UploadFile,
        user_id: int,
        origin_lng: str,
        origin_lat: str
    ) -> Dict:

            if not self.destination_parse_agent or not self.multi_agent_navigation:
                raise ValueError("服务未正确初始化，缺少必要的Agent组件")

            parse_result = self.destination_parse_agent.process_voice_input(
                audio_file,
                user_id=user_id
            )

            if "error" in parse_result:
                raise ValueError(parse_result["error"])

            voice_text = parse_result.get("voice_text", "")
            destination = parse_result.get("destination", "")
            matched_type = parse_result.get("matched_type", "llm")
            latitude = parse_result.get("latitude")
            longitude = parse_result.get("longitude")

            if not destination:
                raise ValueError("无法从语音中解析出目的地")

            origin = f"经度{origin_lng},纬度{origin_lat}"
            
            if latitude and longitude:
                destination = destination + f"，经度{longitude}，纬度{latitude}"

            navigation_result = await self.multi_agent_navigation.plan_travel(origin, destination)

            route_data = navigation_result.get("route", {})
            weather_data = navigation_result.get("weather", "")
            advice_data = navigation_result.get("advice", "")

            voice_log = VoiceLogCreate(
                user_id=user_id,
                audio_url=audio_file.filename,
                asr_text=voice_text,
                intent_json={
                    "destination": destination,
                    "matched_type": matched_type,
                    "origin": origin
                },
                response_text=advice_data,
                log_time=datetime.now()
            )
            await self.voice_log_service.create_log(voice_log)

            # 创建导航记录
            if latitude and longitude:
                record_data = NavigationRecordCreate(
                    user_id=user_id,
                    start_time=datetime.now(),
                    origin_lat=Decimal(origin_lat),
                    origin_lng=Decimal(origin_lng),
                    dest_lat=Decimal(latitude),
                    dest_lng=Decimal(longitude),
                    dest_name=destination,
                    status=1
                )
                self.navigation_record_service.create_record(record_data)



            return {
                "status": "success",
                "voice_text": voice_text,
                "destination": destination,
                "matched_type": matched_type,
                "navigation_advice": advice_data,
                "route": {
                    "text": route_data.get("text", ""),
                    "origin": route_data.get("origin", origin),
                    "destination": route_data.get("destination", destination),
                    "distance": route_data.get("distance", ""),
                    "duration": route_data.get("duration", ""),
                    "steps": route_data.get("steps", []),
                    "polyline": route_data.get("polyline", "")
                },
                "weather": weather_data,
                "latitude": latitude,
                "longitude": longitude
            }

    # async def plan_route(self, origin: str, destination: str, priority: str = "elderly_friendly"):
    #     params = {
    #         "origin": origin,
    #         "destination": destination,
    #         "key": self.amap_key,
    #         "extensions": "all"
    #     }

    #     response = await self.client.get(f"{self.base_url}/direction/walking", params=params)
    #     route_data = response.json()

    #     if priority == "elderly_friendly":
    #         route_data = self._filter_elderly_friendly(route_data)
    #     elif priority == "time":
    #         route_data = self._filter_fastest_route(route_data)
    #     elif priority == "distance":
    #         route_data = self._filter_shortest_route(route_data)

    #     return route_data

    # def _filter_elderly_friendly(self, route_data: dict) -> dict:
    #     if "route" not in route_data:
    #         return route_data

    #     route = route_data["route"]
    #     if "paths" not in route:
    #         return route_data

    #     paths = route["paths"]
    #     if not paths:
    #         return route_data

    #     best_path = None
    #     best_score = -1

    #     for path in paths:
    #         score = self._calculate_elderly_friendly_score(path)
    #         if score > best_score:
    #             best_score = score
    #             best_path = path

    #     route["paths"] = [best_path] if best_path else []
    #     route_data["route"] = route

    #     return route_data

    # def _calculate_elderly_friendly_score(self, path: dict) -> float:
    #     score = 0.0

    #     score += 100.0

    #     distance = path.get("distance", 0)
    #     distance = float(distance) if distance else 0
    #     score -= distance / 100

    #     duration = path.get("duration", 0)
    #     duration = float(duration) if duration else 0
    #     score -= duration / 60

    #     steps = path.get("steps", [])
    #     step_count = len(steps)
    #     score -= step_count * 0.5

    #     for step in steps:
    #         instruction = step.get("instruction", "")
    #         if "阶梯" in instruction:
    #             score -= 10.0
    #         if "上坡" in instruction:
    #             score -= 5.0
    #         if "下坡" in instruction:
    #             score -= 3.0

    #     return max(0, score)

    # def _filter_fastest_route(self, route_data: dict) -> dict:
    #     if "route" not in route_data:
    #         return route_data

    #     route = route_data["route"]
    #     if "paths" not in route:
    #         return route_data

    #     paths = route["paths"]
    #     if not paths:
    #         return route_data

    #     fastest_path = None
    #     min_duration = float('inf')

    #     for path in paths:
    #         duration = path.get("duration", 0)
    #         duration = float(duration) if duration else 0
    #         if duration < min_duration:
    #             min_duration = duration
    #             fastest_path = path

    #     route["paths"] = [fastest_path] if fastest_path else []
    #     route_data["route"] = route

    #     return route_data

    # def _filter_shortest_route(self, route_data: dict) -> dict:
    #     if "route" not in route_data:
    #         return route_data

    #     route = route_data["route"]
    #     if "paths" not in route:
    #         return route_data

    #     paths = route["paths"]
    #     if not paths:
    #         return route_data

    #     shortest_path = None
    #     min_distance = float('inf')

    #     for path in paths:
    #         distance = path.get("distance", 0)
    #         distance = float(distance) if distance else 0
    #         if distance < min_distance:
    #             min_distance = distance
    #             shortest_path = path

    #     route["paths"] = [shortest_path] if shortest_path else []
    #     route_data["route"] = route

    #     return route_data