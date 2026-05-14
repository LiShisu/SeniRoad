from fastapi import APIRouter, Depends, status, UploadFile, File
from app.agent.tools.speech_to_text import process_speech_to_text
from app.agent.tools.text_to_speech import process_text_to_speech
# from app.schemas.speech import TextToSpeechRequest
from typing import Dict
import base64
import os
from app.schemas.base import Result
from app.schemas.speech import (
    SpeechSynthesisRequest,
    SpeechSynthesisResponse,
    SpeechRecognitionResponse
)
from app.services.speech import SpeechService
from app.dependencies import get_current_active_user, get_speech_service
from app.models import User

router = APIRouter()

# 1. 语音转文本 (原 /speech-to-text)
@router.post(
    "/asr", 
    response_model=Result[SpeechRecognitionResponse], 
    status_code=status.HTTP_201_CREATED, 
    tags=["语音服务"]
)
async def create_speech_recognition(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user), # 【权限控制】401防护
    speech_service: SpeechService = Depends(get_speech_service)
):
    """
    创建语音识别 (STT)
    - 接收前端录音文件，返回识别出的文本。
    """
    data = await speech_service.recognize_speech(audio_file)
    return Result(code=200, message="语音识别成功", data=data)

# 2. 文本转语音 (原 /text-to-speech)
@router.post(
    "/tts", 
    response_model=Result[SpeechSynthesisResponse], 
    status_code=status.HTTP_201_CREATED, 
    tags=["语音服务"]
)
async def create_speech_synthesis(
    request: SpeechSynthesisRequest,
    current_user: User = Depends(get_current_active_user), # 【权限控制】401防护
    speech_service: SpeechService = Depends(get_speech_service)
):
    """
    创建语音合成 (TTS)
    - 接收文本内容，返回 Base64 编码的音频流数据。
    """
    data = await speech_service.synthesize_speech(request.text)
    return Result(code=200, message="语音合成成功", data=data)