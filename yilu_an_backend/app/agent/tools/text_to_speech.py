from langchain_core.tools import tool
from dashscope.audio.tts_v2 import SpeechSynthesizer
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
        # 创建临时文件
        with tempfile.NamedTemporaryFile(dir=settings.TEMP_DIR, delete=False, suffix=".mp3") as temp_file:
            temp_file_path = temp_file.name
        
        # 调用阿里云 TTS API
        # 使用 dashscope tts_v2 SpeechSynthesizer
        result = SpeechSynthesizer.call(model='cosyvoice-v2', text=text)
        
        if result.status_code == 200:
            # 保存音频文件
            for frame in result.get_audio_frame():
                with open(temp_file_path, 'ab') as f:
                    f.write(frame)
            return temp_file_path
        else:
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return f"TTS Error: {result.message}"
    except Exception as e:
        # 确保临时文件被删除
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return f"TTS Error: {str(e)}"
