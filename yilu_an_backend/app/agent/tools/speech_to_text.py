from langchain_core.tools import tool
from dashscope.audio.asr import Recognition
from fastapi import UploadFile
from app.config import settings
import tempfile
import os

@tool
def speech_to_text(audio_file: UploadFile) -> str:
    """将前端上传的音频文件转换为文本"""
    try:
        # 确保 temp 目录存在
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        
        # 保存上传的音频文件为临时文件
        with tempfile.NamedTemporaryFile(dir=settings.TEMP_DIR, delete=False, suffix=".wav") as temp_file:
            content = audio_file.file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 调用语音识别API
        recognition = Recognition(
            model="paraformer-realtime-v2",
            file_urls=[temp_file_path]
        )
        result = recognition.call()
        
        # 删除临时文件
        os.unlink(temp_file_path)
        
        return result.output["text"] if result.status_code == 200 else "ASR Error"
    except Exception as e:
        # 确保临时文件被删除
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return f"ASR Error: {str(e)}"