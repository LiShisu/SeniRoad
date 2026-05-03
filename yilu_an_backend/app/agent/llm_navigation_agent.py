from app.agent.tools.navigation import tools
from app.agent.tools.speech_to_text import speech_to_text
from app.llmclient import text_llm
from fastapi import UploadFile
from typing import Dict, Any
from langchain import agents

# 废弃导航Agent，使用多Agent导航系统
class LLMNavigationAgent:
    def __init__(self):
        self.llm = text_llm
        self.system_prompt = """你是一个智能导航助手，专门为老年人提供导航服务。
        
        你的功能包括：
        1. 处理语音输入，识别用户的目的地
        2. 获取当前位置
        3. 规划到目的地的路线，优先考虑老年人友好的路线
        4. 提供清晰的导航指引
        
        你可以使用以下工具：
        - get_destination_coordinates: 获取目的地的经纬度坐标，参数为：
            address: 目的地地址或名称，如"天安门"
            city: 城市名称（可选），有助于提高解析准确性
        - plan_route: 规划导航路线，参数为：
            origin: 起点坐标，格式为"经度,纬度"，
            destination: 终点坐标，格式为"经度,纬度"或目的地名称，
            priority: 优先级，可选值为"elderly_friendly"（默认）、"time"、"distance"
        
        请根据用户的请求，合理使用工具来完成导航任务。"""
        
        self.agent = agents.create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=self.system_prompt,
            verbose=True
        )
    
    async def process_input(self, input_data: str = None, audio_file: UploadFile = None, current_location: str = None) -> Dict[str, Any]:
        """处理输入并规划导航路线

        Args:
            input_data: 文本输入
            audio_file: 上传的音频文件
            current_location: 当前位置坐标，格式为"经度,纬度"，由前端传入

        Returns:
            Dict: 包含导航路线信息的字典
        """
        try:
            if audio_file:
                voice_text = speech_to_text(audio_file)

                if "Error" in voice_text:
                    return {"error": voice_text}

                user_message = f"用户想要导航到：{voice_text}"
                if current_location:
                    user_message += f"，当前位置：{current_location}"

                result = await self.agent.ainvoke({
                    "messages": [("user", user_message)]
                })

                messages = result.get("messages", [])
                output = messages[-1].content if messages else ""

                return {
                    "voice_text": voice_text,
                    "response": output
                }
            elif input_data:
                user_message = f"用户想要导航到：{input_data}"
                if current_location:
                    user_message += f"，当前位置：{current_location}"

                result = await self.agent.ainvoke({
                    "messages": [("user", user_message)]
                })

                messages = result.get("messages", [])
                output = messages[-1].content if messages else ""

                return {
                    "input_text": input_data,
                    "response": output
                }
            else:
                return {"error": "请提供文本输入或音频文件"}
        except Exception as e:
            return {
                "error": f"处理失败: {str(e)}"
            }