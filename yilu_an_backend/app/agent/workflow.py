"""
智能导航LangGraph工作流

基于LangGraph构建的智能导航工作流系统。
工作流架构：
[目的地解析] -> [路线查询 + 天气查询（并行）] -> [出行建议]
"""

import asyncio
import json
from typing import Dict, Any, AsyncGenerator, Optional
from langgraph.graph import StateGraph, END
from app.agent.schemas import NavigationWorkflowState, RouteResult, WeatherResult
from app.agent.nodes.destination_parse_node import destination_parse_node
from app.agent.nodes.route_node import route_query_node
from app.agent.nodes.weather_node import weather_query_node
from app.agent.nodes.advisor_node import advisor_node
from app.services.favorite_place import FavoritePlaceService


def create_navigation_graph(
    favorite_place_service: Optional[FavoritePlaceService] = None
):
    """创建导航工作流图

    Args:
        favorite_place_service: 收藏地点服务实例

    Returns:
        编译后的LangGraph图
    """
    workflow = StateGraph(NavigationWorkflowState)

    # 添加节点
    workflow.add_node("destination_parse", lambda state: destination_parse_node(state, favorite_place_service))
    workflow.add_node("route_query", route_query_node)
    workflow.add_node("weather_query", weather_query_node)
    workflow.add_node("advisor", advisor_node)

    # 设置入口点
    workflow.set_entry_point("destination_parse")

    # 目的地解析完成后，并行执行路线查询和天气查询
    workflow.add_edge("destination_parse", "route_query")
    workflow.add_edge("destination_parse", "weather_query")

    # 路线和天气查询完成后，进入出行建议节点
    workflow.add_edge("route_query", "advisor")
    workflow.add_edge("weather_query", "advisor")

    # 出行建议节点完成后结束
    workflow.add_edge("advisor", END)

    return workflow.compile()


async def execute_navigation_workflow(
    origin_lng: str,
    origin_lat: str,
    user_id: int,
    destination_name: str = "",
    destination_lng: Optional[str] = None,
    destination_lat: Optional[str] = None,
    favorite_place_id: Optional[int] = None,
    audio_file = None,
    favorite_place_service: Optional[FavoritePlaceService] = None
) -> Dict[str, Any]:
    """执行导航工作流（非流式）

    Args:
        origin_lng: 起点经度
        origin_lat: 起点纬度
        user_id: 用户ID
        destination_name: 目的地名称
        destination_lng: 目的地经度
        destination_lat: 目的地纬度
        favorite_place_id: 收藏地点ID
        audio_file: 音频文件
        favorite_place_service: 收藏地点服务

    Returns:
        包含路线、天气和出行建议的字典
    """
    graph = create_navigation_graph(favorite_place_service)

    initial_state = NavigationWorkflowState(
        messages=[],
        user_id=user_id,
        origin_lng=origin_lng,
        origin_lat=origin_lat,
        destination_name=destination_name,
        destination_lng=destination_lng,
        destination_lat=destination_lat,
        favorite_place_id=favorite_place_id,
        audio_file=audio_file,
        route_result=RouteResult(),
        weather_result=WeatherResult(),
        final_advice="",
        matched_type="",
        voice_text=""
    )

    try:
        result = await graph.ainvoke(initial_state)
        return {
            "route": result.route_result.model_dump(),
            "weather": result.weather_result.model_dump(),
            "advice": result.final_advice,
            "destination_name": result.destination_name,
            "matched_type": result.matched_type,
            "voice_text": result.voice_text,
            "destination_lng": result.destination_lng,
            "destination_lat": result.destination_lat
        }
    except Exception as e:
        return {
            "route": RouteResult().model_dump(),
            "weather": WeatherResult().model_dump(),
            "advice": f"出行规划失败: {str(e)}",
            "destination_name": destination_name,
            "matched_type": "",
            "voice_text": "",
            "destination_lng": destination_lng,
            "destination_lat": destination_lat
        }


async def execute_navigation_workflow_stream(
    origin_lng: str,
    origin_lat: str,
    user_id: int,
    destination_name: str = "",
    destination_lng: Optional[str] = None,
    destination_lat: Optional[str] = None,
    favorite_place_id: Optional[int] = None,
    audio_file = None,
    favorite_place_service: Optional[FavoritePlaceService] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """执行导航工作流（流式）

    并行执行路线查询和天气查询，结果实时推送。

    Args:
        origin_lng: 起点经度
        origin_lat: 起点纬度
        user_id: 用户ID
        destination_name: 目的地名称
        destination_lng: 目的地经度
        destination_lat: 目的地纬度
        favorite_place_id: 收藏地点ID
        audio_file: 音频文件
        favorite_place_service: 收藏地点服务

    Yields:
        包含不同类型结果的字典事件
    """
    # graph = create_navigation_graph(favorite_place_service)

    initial_state = NavigationWorkflowState(
        messages=[],
        user_id=user_id,
        origin_lng=origin_lng,
        origin_lat=origin_lat,
        destination_name=destination_name,
        destination_lng=destination_lng,
        destination_lat=destination_lat,
        favorite_place_id=favorite_place_id,
        audio_file=audio_file,
        route_result=RouteResult().model_dump(),
        weather_result=WeatherResult().model_dump(),
        final_advice="",
        matched_type="",
        voice_text=""
    )

    # 第一步：目的地解析
    try:
        parse_result = await destination_parse_node(initial_state, favorite_place_service)
        
        # 更新状态 - 使用 model_copy 方法更新BaseModel
        updated_state = initial_state.model_copy(update=parse_result)
        
        yield {
            "event": "destination",
            "data": {
                "destination": parse_result.get("destination_name", ""),
                "voice_text": parse_result.get("voice_text", ""),
                "matched_type": parse_result.get("matched_type", ""),
                "destination_lng": parse_result.get("destination_lng"),
                "destination_lat": parse_result.get("destination_lat")
            }
        }
    except Exception as e:
        yield {"event": "error", "data": {"error": f"目的地解析失败: {str(e)}"}}
        return

    # 第二步：并行执行路线和天气查询
    route_done = False
    weather_done = False
    route_pushed = False
    weather_pushed = False
    route_result_data: Optional[RouteResult] = None
    weather_result_data: Optional[WeatherResult] = None

    async def run_route():
        nonlocal route_result_data, route_done
        route_result_data = await route_query_node(updated_state)
        route_done = True

    async def run_weather():
        nonlocal weather_result_data, weather_done
        weather_result_data = await weather_query_node(updated_state)
        weather_done = True

    route_task = asyncio.create_task(run_route())
    weather_task = asyncio.create_task(run_weather())

    # 等待并实时推送结果
    while not (route_done and weather_done):
        await asyncio.sleep(0.5)

        if route_done and route_result_data is not None and not route_pushed:
            yield {"event": "route", "data": route_result_data.model_dump()}
            route_pushed = True

        if weather_done and weather_result_data is not None and not weather_pushed:
            yield {"event": "weather", "data": weather_result_data.model_dump()}
            weather_pushed = True

    await asyncio.gather(route_task, weather_task)

    # 确保获取到结果数据
    if route_result_data is None:
        route_result_data = RouteResult(text="路线查询未返回结果")
    if weather_result_data is None:
        weather_result_data = WeatherResult(weather_text="天气查询未返回结果")

    # 第三步：生成出行建议
    # 更新状态，包含路线和天气结果
    advisor_state = updated_state.model_copy(update={
        "route_result": route_result_data,
        "weather_result": weather_result_data
    })

    try:
        advisor_result = await advisor_node(advisor_state)
        yield {"event": "advice", "data": advisor_result.model_dump()}
    except Exception as e:
        yield {"event": "error", "data": {"error": f"生成出行建议失败: {str(e)}"}}

    yield {"event": "complete", "data": {"status": "done"}}
