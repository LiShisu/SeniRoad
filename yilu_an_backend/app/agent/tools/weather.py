from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气"""
    # 这里模拟一个返回结果，实际可接入天气 API
    return f"{city}今天是晴天，气温25度，适合穿短袖。"

# 将工具放入列表
tools = [get_weather]