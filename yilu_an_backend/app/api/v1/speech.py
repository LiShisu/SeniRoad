from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.agent.tools.speech_to_text import speech_to_text
from app.agent.tools.text_to_speech import text_to_speech
from app.schemas.speech import TextToSpeechRequest
from typing import Dict
import base64
import os

router = APIRouter()

@router.post("/speech-to-text")
async def convert_speech_to_text(
    audio_file: UploadFile = File(...)
) -> Dict:
    """将前端上传的语音文件转换为文本
    
    - audio_file: 音频文件（支持wav格式）
    """
    try:
        # 调用语音转文本工具
        text = speech_to_text.invoke(audio_file)
        
        if "Error" in text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=text
            )
        
        return {
            "text": text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音转文本失败: {str(e)}"
        )

@router.post("/text-to-speech")
async def convert_text_to_speech(
    request: TextToSpeechRequest
) -> Dict:
    """将文本转换为语音文件（返回 base64 编码的音频数据）
    
    - text: 需要转换的文本内容（最多500字）
    """
    try:
        # 调用文本转语音工具
        audio_file_path = text_to_speech.invoke(request.text)
        
        if "Error" in audio_file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=audio_file_path
            )
        
        # 读取音频文件并转换为 base64
        with open(audio_file_path, 'rb') as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        
        # 删除临时文件
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        
        return {
            "status": "success",
            "audio_data": audio_data,
            "audio_type": "audio/mpeg"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文本转语音失败: {str(e)}"
        )
