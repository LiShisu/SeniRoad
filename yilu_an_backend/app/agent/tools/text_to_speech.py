from langchain_core.tools import tool
from dashscope.audio.tts_v2 import SpeechSynthesizer
import dashscope
from app.config import settings
import tempfile
import os

@tool
def text_to_speech(text: str) -> str:
    """将文本转换为语音文件
    
    Args:
        text: 需要转换的文本内容
    
    Returns:
        str: 生成的音频文件路径
    """
    try:
        # 设置 DashScope API Key
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        
        # 确保 temp 目录存在
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(dir=settings.TEMP_DIR, delete=False, suffix=".mp3") as temp_file:
            temp_file_path = temp_file.name
        
        # 调用阿里云 TTS API
        # 使用 dashscope tts_v2 SpeechSynthesizer
        synthesizer = SpeechSynthesizer(model='cosyvoice-v2', voice='longxiaochun')
        audio_data = synthesizer.call(text)
        
        if audio_data:
            # 保存音频文件
            with open(temp_file_path, 'wb') as f:
                f.write(audio_data)
            return temp_file_path
        else:
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return f"TTS Error: 音频合成失败"
    except Exception as e:
        # 确保临时文件被删除
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return f"TTS Error: {str(e)}"
