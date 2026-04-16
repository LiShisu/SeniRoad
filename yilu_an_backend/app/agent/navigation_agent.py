from app.services.ai_parser import AIParserService
from app.services.navigation import NavigationService
from fastapi import HTTPException, status
import json
from typing import Dict, List, Optional

class NavigationAgent:
    def __init__(self, ai_parser_service: AIParserService, navigation_service: NavigationService):
        self.ai_parser_service = ai_parser_service
        self.navigation_service = navigation_service
    
    async def process_voice_input(self, audio_file_path: str) -> Dict:
        """处理语音输入并规划导航路线
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            Dict: 包含导航路线信息的字典
        """
        try:
            # 1. 语音转文本
            voice_text = speech_to_text(audio_file_path)
            if voice_text == "ASR Error":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="语音解析失败"
                )
            
            # 2. 提取目的地信息
            destination_info = await self.ai_parser_service.parse_destination(voice_text)
            if not destination_info or "destination" not in destination_info:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无法从语音中提取目的地信息"
                )
            
            destination = destination_info["destination"]
            
            # 3. 规划路线
            route_data = await self.plan_route_by_destination(destination)
            
            return {
                "voice_text": voice_text,
                "destination": destination,
                "route": route_data
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"导航规划失败: {str(e)}"
            )
    
    async def plan_route_by_destination(self, destination: str) -> Dict:
        """根据目的地规划导航路线
        
        Args:
            destination: 目的地名称或地址
            
        Returns:
            Dict: 包含导航路线信息的字典
        """
        try:
            # 1. 获取当前位置（这里假设从设备或其他服务获取）
            current_location = await self._get_current_location()
            
            # 2. 规划路线
            route_data = await self.navigation_service.plan_route(
                origin=current_location,
                destination=destination,
                priority="elderly_friendly"
            )
            
            # 3. 整理路线数据
            formatted_route = self._format_route_data(route_data)
            
            return formatted_route
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"导航规划失败: {str(e)}"
            )
    
    async def _get_current_location(self) -> str:
        """获取当前位置
        
        Returns:
            str: 当前位置坐标，格式为"经度,纬度"
        """
        # 这里应该从设备或其他服务获取当前位置
        # 暂时返回一个默认位置
        return "116.397428,39.90923"
    
    def _format_route_data(self, route_data: Dict) -> Dict:
        """格式化路线数据
        
        Args:
            route_data: 原始路线数据
            
        Returns:
            Dict: 格式化后的路线数据
        """
        # 这里根据前端要求的格式进行整理
        # 假设原始路线数据包含以下字段：
        # - origin: 起点
        # - destination: 终点
        # - waypoints: 途经点
        # - distance: 距离
        # - duration: 预计时间
        # - steps: 导航步骤
        
        formatted_route = {
            "origin": route_data.get("origin", ""),
            "destination": route_data.get("destination", ""),
            "distance": route_data.get("distance", 0),
            "duration": route_data.get("duration", 0),
            "steps": []
        }
        
        # 格式化导航步骤
        if "steps" in route_data:
            for step in route_data["steps"]:
                formatted_step = {
                    "instruction": step.get("instruction", ""),
                    "distance": step.get("distance", 0),
                    "duration": step.get("duration", 0),
                    "polyline": step.get("polyline", "")
                }
                formatted_route["steps"].append(formatted_step)
        
        return formatted_route

# 示例使用
# from app.dependencies import get_ai_parser_service, get_navigation_service
# ai_parser_service = get_ai_parser_service()
# navigation_service = get_navigation_service()
# agent = NavigationAgent(ai_parser_service, navigation_service)
# result = await agent.process_voice_input("path/to/audio.wav")
# print(result)
