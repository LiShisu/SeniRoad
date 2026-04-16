from app.llmclient import text_llm
from typing import Dict, Optional


class AIParserService:
    def __init__(self):
        pass
    
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
            
            # 使用 text_llm 生成响应
            response = text_llm.invoke(prompt)
            
            # 提取目的地信息
            destination = response.content.strip()
            # 去除可能的标点符号和多余的文字
            destination = destination.replace("。", "").replace(".", "").strip()
            return {"destination": destination}
        except Exception as e:
            # 如果解析失败，返回原始输入作为目的地
            return {"destination": user_input}
