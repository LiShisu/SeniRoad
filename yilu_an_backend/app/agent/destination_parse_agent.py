from app.agent.tools.speech_to_text import speech_to_text
from app.llmclient import text_llm
from typing import Dict, Optional

class DestinationParseAgent:
    def __init__(self):
        pass
    
    def process_voice_input(self, audio_file_path: str) -> Dict:
        """处理语音输入并解析目的地

        Args:
            audio_file_path: 音频文件路径

        Returns:
            Dict: 包含解析结果的字典，格式为 {"voice_text": "语音转文本结果", "destination": "目的地名称或地址"}
        """
        try:
            # 1. 语音转文本
            voice_text = speech_to_text(audio_file_path)
            if voice_text == "ASR Error":
                return {"voice_text": "", "destination": "", "error": "语音解析失败"}

            # 2. 解析文本获取目的地
            destination = self._parse_destination(voice_text)
            
            return {"voice_text": voice_text, "destination": destination}
        except Exception as e:
            return {"voice_text": "", "destination": "", "error": str(e)}
    
    def _parse_destination(self, text: str) -> str:
        """从文本中解析目的地

        Args:
            text: 语音转文本的结果

        Returns:
            str: 解析出的目的地
        """
        try:
            # 构建提示词
            prompt = f"请从以下老年人的口语化表达中提取目的地信息，只返回目的地名称或地址，不要包含其他内容：{text}"
            
            # 使用 text_llm 生成响应
            response = text_llm.invoke(prompt)
            
            # 提取目的地信息
            destination = response.content.strip()
            # 去除可能的标点符号和多余的文字
            destination = destination.replace("。", "").replace(".", "").strip()
            
            return destination
        except Exception as e:
            # 如果解析失败，返回原始文本作为目的地
            return text
