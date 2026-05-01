from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.agent.tools.speech_to_text import speech_to_text
from typing import Dict

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
        text = speech_to_text(audio_file)
        
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
