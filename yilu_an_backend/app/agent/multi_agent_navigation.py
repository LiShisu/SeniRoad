"""
智能导航多Agent服务

基于LangChain和LangGraph构建的多智能体协作系统，用于出行规划服务。
系统包含三个专业Agent（路线Agent、天气Agent、顾问Agent）和一个编排Agent（Orchestrator）。

多Agent协作的优势：
1. 专业分工：每个Agent专注于特定领域，提高处理质量
2. 并行执行：路线和天气查询可以同时进行，减少等待时间
3. 可扩展性：可以轻松添加新的专业Agent（如交通Agent、景点Agent）
4. 易于维护：各Agent独立开发测试，降低代码耦合度
5. 智能编排：Orchestrator根据任务需求动态调度资源

架构图：
                                    ┌─────────────────┐
                                    │ Orchestrator    │
                                    │   (编排器)      │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
           ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
           │   RouteAgent    │      │  WeatherAgent   │      │  AdvisorAgent   │
           │    (路线Agent)   │      │   (天气Agent)   │      │   (顾问Agent)   │
           └────────┬────────┘      └────────┬────────┘      └────────┬────────┘
                    │                        │                        │
                    │ 路线工具                │ 天气工具               │ 无工具
                    │ (高德MCP)              │ (高德MCP)              │ (LLM推理)
                    ▼                        ▼                        ▼
           ┌─────────────────────────────────────────────────────────────────┐
           │                      整合结果返回用户                              │
           └─────────────────────────────────────────────────────────────────┘
"""

import asyncio
from typing import TypedDict, Annotated, Sequence, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import settings
from app.llmclient import text_llm


class TravelState(TypedDict):
    """出行规划状态类

    包含多Agent协作过程中需要传递的所有状态信息：
    - messages: 对话历史
    - origin: 出发地
    - destination: 目的地
    - route_result: 路线规划结果
    - weather_result: 天气查询结果
    - final_advice: 最终出行建议
    """
    messages: Annotated[Sequence[BaseMessage], "messages"]
    origin: str
    destination: str
    route_result: Dict[str, Any]
    weather_result: str
    final_advice: str


route_tools = []
weather_tools = []
all_tools = []


async def setup_mcp_tools():
    """初始化高德MCP工具

    使用langchain_mcp_adapters连接高德官方MCP服务（SSE接入），
    并根据工具名称关键字将工具分类给RouteAgent和WeatherAgent。
    """
    global route_tools, weather_tools, all_tools

    if not settings.AMAP_API_KEY:
        print("警告: AMAP_API_KEY 未设置，将使用空工具集")
        return

    mcp_client = MultiServerMCPClient(
        {
            "amap": {
                "url": f"https://mcp.amap.com/sse?key={settings.AMAP_API_KEY}",
                "transport": "sse"
            }
        }
    )

    all_tools = await mcp_client.get_tools()

    for tool in all_tools:
        tool_name = tool.name.lower()
        if any(keyword in tool_name for keyword in ["weather", "天气"]):
            weather_tools.append(tool)
        elif any(keyword in tool_name for keyword in [
            "direction", "route", "driving", "walking", "bicycling",
            "transit", "geocode", "geo", "navigation", "path", "routeplanning"
        ]):
            route_tools.append(tool)

    print(f"已加载 {len(all_tools)} 个高德MCP工具")
    print(f"路线相关工具 ({len(route_tools)}): {[t.name for t in route_tools]}")
    print(f"天气相关工具 ({len(weather_tools)}): {[t.name for t in weather_tools]}")


route_agent = None
weather_agent = None
advisor_agent = None
_agents_initialized = False


def create_agents():
    """创建三个专业Agent

    每个Agent使用create_agent工厂函数创建，绑定不同的工具集和系统提示词。
    """
    global route_agent, weather_agent, advisor_agent, _agents_initialized

    if _agents_initialized:
        return

    route_system_prompt = """你是一个专业的路线规划Agent，擅长规划出行路线。

你的职责：
- 根据用户提供的出发地和目的地，若提供经纬度则使用经纬度，否则根据地址规划最优路线
- 支持多种出行方式：驾车、步行、骑行、公交
- 提供详细的路线步骤、距离、预计时间等信息
- 用中文友好地描述路线信息

当调用路线规划工具时：
1. 首先使用地理编码工具将地址转换为坐标（如果需要）
2. 然后使用路径规划工具获取路线信息
3. 将结果整理成结构化的中文描述

记住：你只能使用路线相关的工具，不要尝试调用天气或其他工具。"""

    weather_system_prompt = """你是一个专业的天气查询Agent，擅长查询目的地天气信息。

你的职责：
- 查询用户指定城市的当前天气情况
- 提供天气现象，温度、风力、湿度、空气质量等信息
- 根据天气情况给出简单的出行建议（如：适合外出、记得带伞等）

当调用天气查询工具时：
1. 使用天气查询工具获取实时天气数据
2. 将结果整理成结构化的中文描述

记住：你只能使用天气相关的工具，不要尝试调用路线规划或其他工具。"""

    advisor_system_prompt = """你是一个贴心的出行顾问Agent，擅长综合分析并给出出行建议。

你的职责：
- 接收路线Agent提供的路线信息
- 接收WeatherAgent提供的天气信息
- 综合两者信息，生成全面的外出注意事项清单

生成的建议应包含：
1. 穿衣建议（根据天气温度）
2. 随身物品清单（根据天气：雨伞、防晒霜等）
3. 安全提醒（如:路况、天气对出行的注意事项）
4. 最佳出行时段建议
5. 其他贴心小贴士

你的输出应该：
- 语言亲切友好，像一个贴心的助手
- 结构清晰，使用emoji增加可读性
- 重点突出老人出行需要特别注意的事项

注意：你不需要调用任何工具，完全基于提供的路线和天气信息进行推理和建议。"""

    route_agent = create_agent(
        model=text_llm,
        tools=route_tools,
        system_prompt=route_system_prompt
    )

    weather_agent = create_agent(
        model=text_llm,
        tools=weather_tools,
        system_prompt=weather_system_prompt
    )

    advisor_agent = create_agent(
        model=text_llm,
        tools=[],
        system_prompt=advisor_system_prompt
    )

    _agents_initialized = True


async def route_node(state: TravelState) -> dict:
    """路线规划节点

    由Orchestrator调度，调用RouteAgent执行路线规划。
    将路线结果存入state.route_result。

    Args:
        state: 当前出行状态，包含出发地和目的地

    Returns:
        dict: 更新后的route_result
    """
    origin = state["origin"]
    destination = state["destination"]

    route_messages = [
        HumanMessage(content=f"请帮我规划从 {origin} 到 {destination} 的路线，"
                              f"考虑老人出行需求，提供多种出行方式的选择。")
    ]

    try:
        result = await route_agent.ainvoke({"messages": route_messages})
        route_text = result["messages"][-1].content

        route_data = _parse_route_result(route_text, origin, destination)

    except Exception as e:
        route_data = {
            "text": f"路线规划失败: {str(e)}",
            "origin": origin,
            "destination": destination,
            "distance": "",
            "duration": "",
            "steps": [],
            "polyline": ""
        }

    return {"route_result": route_data}


def _parse_route_result(route_text: str, origin: str, destination: str) -> Dict[str, Any]:
    import re

    distance_match = re.search(r"距离[：:]\s*(\d+[\u4e00-\u9fa5a-zA-Z]+)", route_text)
    duration_match = re.search(r"预计[时长]?[：:]\s*(\d+[\u4e00-\u9fa5a-zA-Z]+)", route_text)

    distance = distance_match.group(1) if distance_match else ""
    duration = duration_match.group(1) if duration_match else ""

    steps = []
    step_matches = re.findall(r"第(\d+)步[：:]?\s*([^。]+)", route_text)
    for step_num, instruction in step_matches:
        steps.append({
            "step_number": int(step_num),
            "instruction": instruction.strip(),
            "distance": "",
            "duration": "",
            "polyline": ""
        })

    polyline_match = re.search(r"坐标[：:]\s*\[([^\]]+)\]", route_text)
    polyline = polyline_match.group(1) if polyline_match else ""

    return {
        "text": route_text,
        "origin": origin,
        "destination": destination,
        "distance": distance,
        "duration": duration,
        "steps": steps,
        "polyline": polyline
    }


async def weather_node(state: TravelState) -> dict:
    """天气查询节点

    由Orchestrator调度，调用WeatherAgent查询目的地天气。
    将天气结果存入state.weather_result。

    Args:
        state: 当前出行状态，包含目的地

    Returns:
        dict: 更新后的weather_result
    """
    destination = state["destination"]

    weather_messages = [
        HumanMessage(content=f"请帮我查询 {destination} 的当前天气情况，"
                              f"包括温度、天气现象、风力、湿度等信息。")
    ]

    try:
        result = await weather_agent.ainvoke({"messages": weather_messages})
        weather_result = result["messages"][-1].content
    except Exception as e:
        weather_result = f"天气查询失败: {str(e)}"

    return {"weather_result": weather_result}


async def advisor_node(state: TravelState) -> dict:
    """出行顾问节点

    由Orchestrator调度，调用AdvisorAgent综合路线和天气信息生成出行建议。
    将最终建议存入state.final_advice和state.messages。

    Args:
        state: 当前出行状态，包含route_result和weather_result

    Returns:
        dict: 更新后的final_advice和messages
    """
    route_result = state["route_result"]
    weather_result = state["weather_result"]
    origin = state["origin"]
    destination = state["destination"]

    route_text = route_result.get("text", "") if isinstance(route_result, dict) else route_result

    advisor_messages = [
        HumanMessage(content=f"""请根据以下信息，为老人出行生成一份完整的注意事项清单：

出发地：{origin}
目的地：{destination}

路线信息：
{route_text}

天气信息：
{weather_result}

请综合以上信息，生成一份贴心、全面的出行建议。""")
    ]

    try:
        result = await advisor_agent.ainvoke({"messages": advisor_messages})
        final_advice = result["messages"][-1].content
    except Exception as e:
        final_advice = f"生成出行建议失败: {str(e)}"

    return {
        "final_advice": final_advice,
        "messages": state["messages"] + [AIMessage(content=final_advice)]
    }


def route_should_continue(state: TravelState) -> str:
    if state.get("weather_result"):
        return "advisor"
    return "weather"


def weather_should_continue(state: TravelState) -> str:
    if state.get("route_result"):
        return "advisor"
    return END


def create_travel_graph() -> StateGraph:
    workflow = StateGraph(TravelState)

    workflow.add_node("route", route_node)
    workflow.add_node("weather", weather_node)
    workflow.add_node("advisor", advisor_node)

    workflow.set_entry_point("route")

    workflow.add_conditional_edges(
        "route",
        route_should_continue,
        {
            "advisor": "advisor",
            "weather": "weather"
        }
    )

    workflow.add_conditional_edges(
        "weather",
        weather_should_continue,
        {
            "advisor": "advisor",
            "END": END
        }
    )

    workflow.add_edge("advisor", END)

    return workflow.compile()


async def plan_travel(origin: str, destination: str) -> Dict[str, Any]:
    """出行规划主函数，使用 Orchestrator(LangGraph 动态调度)

    用户入口函数，接收出发地和目的地，返回完整的出行建议。

    Args:
        origin: 出发地
        destination: 目的地

    Returns:
        str: 包含路线、天气和出行建议的完整回复
    """
    graph = create_travel_graph()

    initial_state = TravelState(
        messages=[HumanMessage(content=f"我需要从 {origin} 到 {destination} 的出行规划")],
        origin=origin,
        destination=destination,
        route_result={},
        weather_result="",
        final_advice=""
    )

    result = await graph.ainvoke(initial_state)

    return {
        "route": result["route_result"],
        "weather": result["weather_result"],
        "advice": result["final_advice"]
    }


async def plan_travel_parallel(origin: str, destination: str) -> Dict[str, Any]:
    """出行规划主函数（并行优化版本）

    使用并行执行优化：同时调用RouteAgent和WeatherAgent，
    然后再调用AdvisorAgent整合结果。

    Args:
        origin: 出发地
        destination: 目的地

    Returns:
        str: 包含路线、天气和出行建议的完整回复
    """

    route_task = route_node(TravelState(
        messages=[],
        origin=origin,
        destination=destination,
        route_result={},
        weather_result="",
        final_advice=""
    ))

    weather_task = weather_node(TravelState(
        messages=[],
        origin=origin,
        destination=destination,
        route_result={},
        weather_result="",
        final_advice=""
    ))

    route_result, weather_result = await asyncio.gather(route_task, weather_task)

    combined_state = TravelState(
        messages=[],
        origin=origin,
        destination=destination,
        route_result=route_result.get("route_result", {}),
        weather_result=weather_result.get("weather_result", ""),
        final_advice=""
    )

    advisor_result = await advisor_node(combined_state)

    return {
        "route": combined_state["route_result"],
        "weather": combined_state["weather_result"],
        "advice": advisor_result.get("final_advice", "抱歉，无法生成出行建议。")
    }


class MultiAgentNavigation:
    _initialized = False

    def __init__(self):
        pass

    async def plan_travel(self, origin: str, destination: str) -> Dict[str, Any]:
        return await plan_travel_parallel(origin, destination)
# async def main():
#     """主函数 - 演示完整的多Agent协作流程

#     示例：从北京市朝阳区到杭州西湖
#     """
#     print("=" * 60)
#     print("🧭 智能导航多Agent服务演示")
#     print("=" * 60)

#     print("\n📡 正在初始化高德MCP工具...")
#     await setup_mcp_tools()

#     print("\n🤖 正在创建专业Agent...")
#     create_agents()

#     origin = "北京市朝阳区"
#     destination = "杭州西湖"

#     print(f"\n📍 出发地：{origin}")
#     print(f"📍 目的地：{destination}")
#     print("\n" + "-" * 60)

#     print("\n🚀 开始执行多Agent协作规划...")
#     print("   ├── route_node: 正在规划路线...")
#     print("   ├── weather_node: 正在查询天气...")
#     print("   └── (两者并行执行)")
#     print()

#     final_advice = await plan_travel_parallel(origin, destination)

#     print("\n" + "=" * 60)
#     print("📋 出行建议清单")
#     print("=" * 60)
#     print(final_advice)
#     print("=" * 60)

#     return final_advice


# if __name__ == "__main__":
#     asyncio.run(main())


