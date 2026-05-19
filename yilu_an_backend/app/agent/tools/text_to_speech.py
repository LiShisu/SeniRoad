import logging
from app.llmclient import create_tts_synthesizer

logger = logging.getLogger(__name__)

async def process_text_to_speech(text: str) -> bytes | str:
    """将文本转换为语音，严谨处理 SDK 响应"""
    try:
        synthesizer = create_tts_synthesizer()
        
        logger.info(f"开始 TTS 合成，文本长度: {len(text)}")
        audio_data = synthesizer.call(text)
        logger.info(f"TTS 调用完成，返回值类型: {type(audio_data)}")
        
        if isinstance(audio_data, bytes):
            logger.info(f"获取到二进制音频数据，长度: {len(audio_data)} bytes")
            return audio_data
        # elif isinstance(audio_data, str):
        #     # 返回的是 URL（某些模型可能返回 URL）
        #     logger.warning(f"返回的是 URL: {audio_data}")
        #     return audio_data
        # elif hasattr(audio_data, 'get_audio_data'):
        #     # SpeechSynthesisResult 对象
        #     audio_bytes = audio_data.get_audio_data()
        #     if audio_bytes:
        #         logger.info(f"从 SpeechSynthesisResult 获取到二进制数据，长度: {len(audio_bytes)} bytes")
        #         return audio_bytes
        #     else:
        #         response_msg = audio_data.get_response() if hasattr(audio_data, 'get_response') else "未知错误"
        #         logger.error(f"TTS 合成失败: {response_msg}")
        #         return f"Error: TTS 合成失败，阿里云未返回音频数据 - {response_msg}"
        else:
            logger.error(f"TTS 返回类型不支持: {type(audio_data)}")
            return f"Error: TTS 返回类型不支持 - {type(audio_data)}"
            
    except Exception as e:
        logger.error(f"TTS 异常: {str(e)}", exc_info=True)
        return f"Error: 内部执行异常 - {str(e)}"