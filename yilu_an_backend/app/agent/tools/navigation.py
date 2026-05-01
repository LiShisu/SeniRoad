from langchain_core.tools import tool
from typing import Dict
from httpx import AsyncClient
from app.config import settings

AMAP_BASE_URL = "https://restapi.amap.com/v3"

@tool
async def get_destination_coordinates(address: str, city: str = None) -> Dict:
    """获取目的地的经纬度坐标

    Args:
        address: 目的地地址或名称，如"天安门"、"北京市朝阳区望京街道"
        city: 城市名称（可选），如"北京"，有助于提高解析准确性

    Returns:
        Dict: 包含经纬度信息的字典，格式为 {"longitude": "经度", "latitude": "纬度", "formatted_address": "格式化地址"}
    """
    try:
        client = AsyncClient()
        params = {
            "key": settings.AMAP_API_KEY,
            "address": address
        }
        if city:
            params["city"] = city
        
        response = await client.get(f"{AMAP_BASE_URL}/geocode/geo", params=params)
        data = response.json()
        
        if data.get("status") == "1" and data.get("geocodes"):
            geocode = data["geocodes"][0]
            return {
                "longitude": float(geocode["location"].split(",")[0]),
                "latitude": float(geocode["location"].split(",")[1]),
                "formatted_address": geocode.get("formatted_address", address),
                "province": geocode.get("province", ""),
                "city": geocode.get("city", ""),
                "district": geocode.get("district", "")
            }
        else:
            return {
                "error": f"无法解析地址: {address}",
                "detail": data.get("info", "未知错误")
            }
    except Exception as e:
        return {
            "error": f"获取坐标失败: {str(e)}"
        }

@tool
async def plan_route(origin: str, destination: str, priority: str = "elderly_friendly") -> Dict:
    """规划导航路线

    Args:
        origin: 起点坐标，格式为"经度,纬度"
        destination: 终点坐标或目的地名称
        priority: 优先级，可选值为"elderly_friendly"（默认）、"time"、"distance"

    Returns:
        Dict: 包含路线信息的字典
    """
    from app.dependencies import get_navigation_service
    navigation_service = get_navigation_service()
    return await navigation_service.plan_route(origin, destination, priority)

# 将工具放入列表
tools = [get_destination_coordinates, plan_route]
