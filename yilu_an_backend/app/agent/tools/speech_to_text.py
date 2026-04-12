from langchain_core.tools import tool
from dashscope.audio.asr import Recognition

@tool
def speech_to_text(audio_file_path: str) -> str:
    """将音频文件转换为文本"""
    recognition = Recognition(
        model="paraformer-realtime-v2",
        file_urls=[audio_file_path]
    )
    result = recognition.call()
    return result.output["text"] if result.status_code == 200 else "ASR Error"