"""
出行建议生成节点

负责调用LLM综合路线和天气信息，生成适老化出行建议。
返回JSON格式与 multi_agent_navigation.py 一致。
"""

import json
from langchain_core.messages import HumanMessage
from app.agent.schemas import NavigationWorkflowState
from app.llmclient import text_llm


async def advisor_node(state: NavigationWorkflowState) -> dict:
    """出行建议节点

    综合路线和天气信息生成出行建议。

    Args:
        state: 当前工作流状态，包含route_result和weather_result

    Returns:
        dict: 更新后的final_advice（JSON格式）
    """
    route_result = state.route_result
    weather_result = state.weather_result
    origin_lng = state.origin_lng
    destination = state.destination_name
    origin_lat = state.origin_lat

    # 构建路线信息文本（BaseModel属性访问）
    distance = route_result.distance if route_result else "0"
    duration = route_result.duration if route_result else "0"

    # 构建天气信息文本（BaseModel属性访问）
    weather_text = (
        f"天气：{weather_result.weather_text}\n"
        f"温度：{weather_result.temperature}\n"
        f"风力：{weather_result.wind}\n"
        f"湿度：{weather_result.humidity}"
    )

    advisor_messages = [
        HumanMessage(content=f"""请根据以下信息，为老人出行生成一份完整的注意事项清单。

出发地：经度{origin_lng},纬度{origin_lat}
目的地：{destination}

路线信息：
距离：{distance}米
预计时间：{duration}秒

天气信息：
{weather_text}

【重要】你必须按照以下JSON格式返回结果，不要包含任何额外文本：

{{
    "clothing_advice": "穿衣建议（如：建议穿薄外套，早晚温差大）",
    "items_to_bring": ["物品1", "物品2", ...],
    "safety_reminders": ["安全提醒1", "安全提醒2", ...],
    "best_time": "最佳出行时段建议（如：建议上午9-11点出行）",
    "tips": ["其他贴心小贴士1", "其他贴心小贴士2", ...]
}}

生成的建议应包含：
1. 穿衣建议（根据天气温度）
2. 随身物品清单（根据天气：雨伞、防晒霜等）
3. 安全提醒（如:路况、天气对出行的注意事项）
4. 最佳出行时段建议
5. 其他贴心小贴士

注意事项：
1. 所有字段都必须返回，不能省略任何字段
2. items_to_bring 是一个数组，包含需要携带的物品
3. safety_reminders 是一个数组，包含安全提醒事项
4. tips 是一个数组，包含其他贴心建议
5. 重点突出老人出行需要特别注意的事项
6. 语言亲切友好，像一个贴心的助手""")
    ]

    try:
        result = await text_llm.ainvoke(advisor_messages)
        final_advice = result.content
        
        # 尝试提取并验证JSON格式
        try:
            json_match = json.loads(final_advice)
            final_advice = json.dumps(json_match, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            json_match = extract_json_from_text(final_advice)
            if json_match:
                final_advice = json.dumps(json_match, ensure_ascii=False)
    except Exception as e:
        final_advice = json.dumps({
            "clothing_advice": "请根据天气情况准备合适的衣物",
            "items_to_bring": ["手机", "钥匙", "钱包"],
            "safety_reminders": ["注意交通安全"],
            "best_time": "建议选择白天出行",
            "tips": ["如有不适请及时休息"]
        }, ensure_ascii=False)

    return {"final_advice": final_advice}


def extract_json_from_text(text: str) -> dict:
    """从文本中提取JSON对象"""
    try:
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception:
        pass
    
    return {
        "clothing_advice": "请根据天气情况准备合适的衣物",
        "items_to_bring": ["手机", "钥匙", "钱包"],
        "safety_reminders": ["注意交通安全"],
        "best_time": "建议选择白天出行",
        "tips": ["如有不适请及时休息"]
    }
