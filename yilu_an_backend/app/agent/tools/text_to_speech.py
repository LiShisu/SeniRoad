import base64
from app.llmclient import create_tts_synthesizer
    
async def process_text_to_speech(text: str) -> str:
    """将文本转换为语音，严谨处理 SDK 响应"""
    try:
        synthesizer = create_tts_synthesizer()
        audio_data = synthesizer.call(text)

        if audio_data:
            # 纯内存操作：秒转 base64 发给前端
            return base64.b64encode(audio_data).decode('utf-8')
        else:
            return "Error: TTS 合成失败，阿里云未返回音频数据"
            
    except Exception as e:
        return f"Error: 内部执行异常 - {str(e)}"