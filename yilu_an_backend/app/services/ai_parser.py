from httpx import AsyncClient
from app.config import settings
import json
from typing import Dict, Optional

class AIParserService:
    def __init__(self):
        self.client = AsyncClient()
        self.qwen_api_key = settings.QWEN_API_KEY
    
    async def parse_destination(self, user_input: str) -> Dict:
        """解析用户输入中的目的地信息
        
        Args:
            user_input: 用户输入的文本，可能是语音转文本的结果
            
        Returns:
            Dict: 包含解析结果的字典，格式为 {"destination": "目的地名称或坐标"}
        """
        try:
            # 构建更精确的提示词
            prompt = f"请从以下老年人的口语化表达中提取目的地信息，只返回目的地名称或地址，不要包含其他内容：{user_input}"
            
            # 发送请求到Qwen API
            response = await self.client.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers={"Authorization": f"Bearer {self.qwen_api_key}"},
                json={
                    "model": "qwen-max", 
                    "input": {"prompt": prompt},
                    "parameters": {
                        "temperature": 0.1,
                        "max_tokens": 100
                    }
                }
            )
            
            # 解析响应
            result = response.json()
            
            # 提取目的地信息
            if "output" in result and "text" in result["output"]:
                destination = result["output"]["text"].strip()
                # 去除可能的标点符号和多余的文字
                destination = destination.replace("。", "").replace(".", "").strip()
                return {"destination": destination}
            else:
                return {"destination": user_input}
        except Exception as e:
            # 如果解析失败，返回原始输入作为目的地
            return {"destination": user_input}
