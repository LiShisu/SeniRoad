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
            # 【核心修改】：现在 process_text_to_speech 直接返回了 base64！
            # 不用再去 open 文件读写，也不用 os.remove 删除文件了，全删掉！
            audio_base64 = await process_text_to_speech(text)
            
            if "Error" in audio_base64:
                raise BusinessException(code=400, message=audio_base64)
            
            return SpeechSynthesisResponse(
                audio_data=audio_base64,
                audio_type="audio/mpeg"
            )
            
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"TTS Error: {str(e)}")
            raise BusinessException(code=500, message=f"系统内部错误：文本转语音异常")