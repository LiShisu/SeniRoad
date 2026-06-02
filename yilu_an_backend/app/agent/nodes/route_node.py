"""
路线查询节点

负责调用高德API获取步行路线规划。
"""

from app.agent.schemas import NavigationWorkflowState, RouteResult
from app.agent.tools.amap_tools import AmapApiTools

# async def route_query_node(state: NavigationWorkflowState) -> RouteResult:
#     """路线查询节点

#     根据起点和终点坐标查询步行路线。

#     Args:
#         state: 当前工作流状态

#     Returns:
#         RouteResult: 更新后的route_result
#     """
#     origin_lng = state.origin_lng
#     origin_lat = state.origin_lat
#     dest_lng = state.destination_lng
#     dest_lat = state.destination_lat

#     # 检查是否有完整的经纬度
#     if not all([origin_lng, origin_lat, dest_lng, dest_lat]):
#         return RouteResult(
#                 text="缺少完整的起点或终点坐标",
#                 origin=f"{origin_lng},{origin_lat}",
#                 destination=f"{dest_lng},{dest_lat}",
#                 distance="0",
#                 duration="0"
#             )
#     # 调用高德API获取路线，直接返回RouteResult对象
#     route_result = await AmapApiTools.get_walking_route(
#         origin_lng=origin_lng,
#         origin_lat=origin_lat,
#         dest_lng=dest_lng,
#         dest_lat=dest_lat
#     )

#     return route_result

async def route_query_node(state: NavigationWorkflowState):
    """路线查询节点

    根据起点和终点坐标查询步行路线。

    Args:
        state: 当前工作流状态

    Returns:
        RouteResult: 更新后的route_result
    """
    origin_lng = state.origin_lng
    origin_lat = state.origin_lat
    dest_lng = state.destination_lng
    dest_lat = state.destination_lat

    # 检查是否有完整的经纬度
    if not all([origin_lng, origin_lat, dest_lng, dest_lat]):
        return RouteResult(
                text="缺少完整的起点或终点坐标",
                origin=f"{origin_lng},{origin_lat}",
                destination=f"{dest_lng},{dest_lat}",
                distance="0",
                duration="0"
            )
    if state.travel_mode == "transit":
        # 如果是公交，调用公交工具 (记得传入城市参数)
        print(f"🟢 route节点开始调用amp工具了")
        route_result = await AmapApiTools.get_transit_route(
            origin_lng=origin_lng, origin_lat=origin_lat,
            dest_lng=dest_lng, dest_lat=dest_lat,
            city=state.city # 需要从某处获取当前城市
        )
    else:
        # 默认步行
        route_result = await AmapApiTools.get_walking_route(
            origin_lng=origin_lng, origin_lat=origin_lat,
            dest_lng=dest_lng, dest_lat=dest_lat
        )

    return route_result