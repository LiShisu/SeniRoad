"""
天气查询节点

负责调用高德API获取目的地天气信息。
返回JSON格式与 multi_agent_navigation.py 一致。
"""

from app.agent.schemas import NavigationWorkflowState, WeatherResult
from app.agent.tools.amap_tools import AmapApiTools


async def weather_query_node(state: NavigationWorkflowState) -> WeatherResult:
    """天气查询节点

    根据目的地坐标查询天气信息。

    Args:
        state: 当前工作流状态

    Returns:
        WeatherResult: 更新后的weather_result（JSON格式）
    """
    origin_lng = state.origin_lng
    origin_lat = state.origin_lat

    # 调用高德API获取天气信息，直接返回WeatherResult对象
    weather_result = await AmapApiTools.get_weather_by_location(
        lng=origin_lng,
        lat=origin_lat,
    )

    return weather_result
