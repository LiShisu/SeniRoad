"""
高德地图API工具模块

封装高德地图API调用，包括路线规划和天气查询功能。
"""

import re
import httpx
from typing import Dict, Any, Optional, Tuple
from app.config import settings
from app.agent.schemas import WeatherResult, RouteResult, RouteStep,TransitLine,TransitRouteResult,TransitSegment
from app.schemas.exception import AmapApiException


class AmapApiTools:
    """高德地图API工具类"""

    BASE_URL = "https://restapi.amap.com/v3"

    @staticmethod
    def parse_coordinates(text: str) -> Tuple[Optional[str], Optional[str]]:
        """从文本中解析经纬度

        Args:
            text: 包含经纬度信息的文本，支持格式：
                  - "经度123.456，纬度78.901"
                  - "经度123.456,纬度78.901"

        Returns:
            Tuple[经度, 纬度] 或 (None, None)
        """
        try:
            match = re.search(r'经度([0-9.]+)[,，]纬度([0-9.]+)', text)
            if match:
                return match.group(1), match.group(2)
        except Exception:
            pass
        return None, None

    @staticmethod
    async def get_walking_route(
        origin_lng: str,
        origin_lat: str,
        dest_lng: str,
        dest_lat: str
    ) -> RouteResult:
        """获取步行路线规划

        Args:
            origin_lng: 起点经度
            origin_lat: 起点纬度
            dest_lng: 终点经度
            dest_lat: 终点纬度

        Returns:
            RouteResult路线规划结果对象
        """
        try:
            params = {
                "origin": f"{origin_lng},{origin_lat}",
                "destination": f"{dest_lng},{dest_lat}",
                "key": settings.AMAP_API_KEY,
                "extensions": "all"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{AmapApiTools.BASE_URL}/direction/walking",
                    params=params,
                    timeout=10.0
                )
                result = response.json()

                if result.get("status") == "1" and result.get("route"):
                    route = result["route"]
                    paths = route.get("paths", [])
                    if not paths:
                        raise AmapApiException("未找到可行的步行路线")

                    path = paths[0]
                    steps = []
                    for step in path.get("steps", []):
                        road = step.get("road", "")
                        if isinstance(road, list):
                            road = ""
                        steps.append(RouteStep(
                            instruction=step.get("instruction", ""),
                            distance=str(step.get("distance", "")),
                            duration=str(step.get("duration", "")),
                            road=road,
                            polyline=step.get("polyline", "")
                        ))

                    polyline = ";".join([step.polyline for step in steps])

                    return RouteResult(
                        text=f"从 {origin_lng},{origin_lat} 到 {dest_lng},{dest_lat} 的路线规划已完成",
                        origin=f"{origin_lng},{origin_lat}",
                        destination=f"{dest_lng},{dest_lat}",
                        distance=path.get("distance", "0"),
                        duration=path.get("duration", "0"),
                        steps=steps,
                        polyline=polyline
                    )
                else:
                    raise AmapApiException(f"路线API返回失败: {result.get('info', '未知错误')}")
        except Exception as e:
            raise AmapApiException(f"获取路线失败: {str(e)}")

    @staticmethod
    async def get_weather_by_location(
        lng: str,
        lat: str
    ) -> WeatherResult:
        """获取天气信息

        Args:
            lng: 经度
            lat: 纬度

        Returns:
            WeatherResult天气信息对象
        """
        try:
            # 如果提供了经纬度，先通过逆地理编码获取城市adcode
            if lng and lat:
                city_adcode = await AmapApiTools._get_city_adcode_by_location(lng, lat)
                if city_adcode:
                    params = {
                        "key": settings.AMAP_API_KEY,
                        "city": city_adcode,
                        "extensions": "base",
                        "output": "json"
                    }
                else:
                    # 如果逆地理编码失败，尝试直接用经纬度查询
                    params = {
                        "key": settings.AMAP_API_KEY,
                        "location": f"{lng},{lat}",
                        "extensions": "base",
                        "output": "json"
                    }
            else:
                raise AmapApiException("无法获取天气信息：缺少位置参数")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{AmapApiTools.BASE_URL}/weather/weatherInfo",
                    params=params,
                    timeout=10.0
                )
                result = response.json()

                if result.get("status") == "1" and result.get("lives"):
                    live = result["lives"][0]
                    return WeatherResult(
                        weather_text=live.get('weather', '未知'),
                        temperature=f"{live.get('temperature', '未知')}℃",
                        wind=f"{live.get('windpower', '未知')}级",
                        humidity=f"{live.get('humidity', '未知')}%"
                    )
                else:
                    raise AmapApiException(f"天气API返回失败: {result.get('info', '未知错误')}")
        except Exception as e:
            raise AmapApiException(f"获取天气失败: {str(e)}")

    @staticmethod
    async def _get_city_adcode_by_location(lng: str, lat: str) -> Optional[str]:
        """通过经纬度获取城市adcode

        Args:
            lng: 经度
            lat: 纬度

        Returns:
            城市adcode，如果获取失败返回None
        """
        try:
            params = {
                "key": settings.AMAP_API_KEY,
                "location": f"{lng},{lat}",
                "output": "json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{AmapApiTools.BASE_URL}/geocode/regeo",
                    params=params,
                    timeout=10.0
                )
                result = response.json()

                if result.get("status") == "1" and result.get("regeocode"):
                    address_component = result["regeocode"].get("addressComponent", {})
                    return address_component.get("adcode")
        except Exception as e:
            print(f"获取城市adcode失败: {e}")
        
        return None
    
    @staticmethod
    async def get_transit_route(
        origin_lng: str, origin_lat: str,
        dest_lng: str, dest_lat: str,
        city: str  # 必须引入城市参数！
    ) -> TransitRouteResult:
        try:
            params = {
                "origin": f"{origin_lng},{origin_lat}",
                "destination": f"{dest_lng},{dest_lat}",
                "city": city,
                "key": settings.AMAP_API_KEY,
                "extensions": "all"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{AmapApiTools.BASE_URL}/direction/transit/integrated",
                    params=params,
                    timeout=10.0
                )
                result = response.json()

                if result.get("status") == "1" and result.get("route"):
                    route = result["route"]
                    transits = route.get("transits", [])
                    if not transits:
                        raise AmapApiException("未找到可行的公交路线")

                    # 通常取第一条推荐方案 (最优选)
                    best_transit = transits[0]
                    segments = []
                    all_polylines = []

                    # 极其繁琐的公交 JSON 解析逻辑（高德的嵌套非常深）
                    for seg in best_transit.get("segments", []):
                        segment_data = TransitSegment()
                        
                        # 1. 解析步行前往车站的部分
                        # walking = seg.get("walking")
                        # walking_steps = []
                        # if walking and walking.get("steps"):
                        #     for step in walking.get("steps"):
                        #         walking_steps.append(RouteStep(
                        #             instruction=step.get("instruction", ""),
                        #             distance=str(step.get("distance", "")),
                        #             duration=str(step.get("duration", "")),
                        #             road=step.get("road", ""),
                        #             polyline=step.get("polyline", "")
                        #         ))
                        walking = seg.get("walking")
                        walking_steps = []
                        if walking and walking.get("steps"):
                            for step in walking.get("steps"):
                                # 🌟 核心修复：提取 road 字段，并强行拦截高德特有的 [] 脏数据
                                road_field = step.get("road", "")
                                if isinstance(road_field, list):
                                    road_field = ""  # 如果是空列表，洗白成空字符串
            
                                walking_steps.append(RouteStep(
                                    instruction=step.get("instruction", ""),
                                    distance=str(step.get("distance", "")),
                                    duration=str(step.get("duration", "")),
                                    road=str(road_field),  # ✅ 现在百分百是安全的字符串了！
                                    polyline=step.get("polyline", "")
                                ))
                            segment_data.walking = {"steps": walking_steps} # 根据你的Schema赋值
                            all_polylines.append(walking.get("polyline", ""))

                        # 2. 解析公交
                        bus = seg.get("bus", {}).get("buslines")
                        if bus and len(bus) > 0:
                            busline = bus[0]
                            segment_data.bus = TransitLine(
                                name=busline.get("name", ""),
                                departure_stop=busline.get("departure_stop", {}).get("name", ""),
                                arrival_stop=busline.get("arrival_stop", {}).get("name", ""),
                                via_num=int(busline.get("via_num", 0)),
                                duration=str(busline.get("duration", "")),
                                polyline=busline.get("polyline", "")
                            )
                            all_polylines.append(busline.get("polyline", ""))
                            
                        segments.append(segment_data)

                    return TransitRouteResult(
                        text=f"为您推荐乘坐...",
                        distance=best_transit.get("distance", "0"),
                        duration=best_transit.get("duration", "0"),
                        segments=segments,
                        polyline=";".join(all_polylines)
                    )
                else:
                    raise AmapApiException("公交API查询失败")
        except Exception as e:
            raise AmapApiException(f"获取公交路线失败: {str(e)}")

