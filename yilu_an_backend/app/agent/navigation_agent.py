from app.agent.destination_parse_agent import DestinationParseAgent
from app.services.navigation import NavigationService
from fastapi import HTTPException, status, UploadFile
from typing import Dict
import tempfile
import os

class NavigationAgent:
    def __init__(self, navigation_service: NavigationService, destination_agent: DestinationParseAgent):
        self.destination_agent = destination_agent
        self.navigation_service = navigation_service

    async def process_voice_input(self, audio_file: UploadFile) -> Dict:
        """处理语音输入并规划导航路线

        Args:
            audio_file: 上传的音频文件

        Returns:
            Dict: 包含导航路线信息的字典
        """
        temp_file_path = None
        try:
            # 保存上传的音频文件为临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                content = audio_file.file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name

            # 1. 语音转文本并解析目的地
            destination_result = self.destination_agent.process_voice_input(temp_file_path)

            if "error" in destination_result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=destination_result["error"]
                )

            destination = destination_result["destination"]

            # 3. 规划路线
            route_data = await self.plan_route_by_destination(destination)

            return {
                "voice_text": destination_result["voice_text"],
                "destination": destination,
                "route": route_data
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"导航规划失败: {str(e)}"
            )
        finally:
            # 确保临时文件被删除
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

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