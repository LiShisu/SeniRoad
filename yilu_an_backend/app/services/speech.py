import base64
import os
import logging
from fastapi import UploadFile
from app.agent.tools.speech_to_text import  process_speech_to_text
from app.agent.tools.text_to_speech import process_text_to_speech
from app.schemas.exception import BusinessException
from app.schemas.speech import SpeechRecognitionResponse, SpeechSynthesisResponse

logger = logging.getLogger(__name__)

class SpeechService:
    async def recognize_speech(self, audio_file: UploadFile) -> SpeechRecognitionResponse:
        """处理语音转文本核心逻辑"""
        try:
            text = await process_speech_to_text(audio_file)
            
            if "Error" in text:
                raise BusinessException(code=400, message=f"语音转文本：语音识别解析失败: {text}")
                
            return SpeechRecognitionResponse(text=text)
            
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"STT Error: {str(e)}")
            raise BusinessException(code=500, message=f"系统内部错误：语音转文本异常")

    async def synthesize_speech(self, text: str) -> SpeechSynthesisResponse:
        try:
            audio_data = await process_text_to_speech(text)
            
            if isinstance(audio_data, str) and "Error" in audio_data:
                raise BusinessException(code=400, message=audio_data)
            
            if not isinstance(audio_data, bytes):
                raise BusinessException(code=500, message="TTS 返回无效的音频数据格式")
            
            return SpeechSynthesisResponse(audio_data=audio_data)
            
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"TTS Error: {str(e)}")
            raise BusinessException(code=500, message=f"系统内部错误：文本转语音异常")