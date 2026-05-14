# from langchain_core.tools import tool
# from app.llmclient import tts_synthesizer
# from app.config import settings
# import tempfile
# import os

# @tool
# def text_to_speech(text: str) -> str:
#     """将文本转换为语音文件

#     Args:
#         text: 需要转换的文本内容

#     Returns:
#         str: 生成的音频文件路径
#     """
#     try:
#         # 确保 temp 目录存在
#         os.makedirs(settings.TEMP_DIR, exist_ok=True)

#         # 创建临时文件
#         with tempfile.NamedTemporaryFile(dir=settings.TEMP_DIR, delete=False, suffix=".mp3") as temp_file:
#             temp_file_path = temp_file.name

#         # 调用阿里云 TTS API
#         audio_data = tts_synthesizer.call(text)

#         if audio_data:
#             # 保存音频文件
#             with open(temp_file_path, 'wb') as f:
#                 f.write(audio_data)
#             return temp_file_path
#         else:
#             # 删除临时文件
#             if os.path.exists(temp_file_path):
#                 os.remove(temp_file_path)
#             return f"TTS Error: 音频合成失败"
#     except Exception as e:
#         # 确保临时文件被删除
#         if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
#             os.remove(temp_file_path)
#         return f"TTS Error: {str(e)}"

import base64
# from app.llmclient import tts_synthesizer
from app.llmclient import create_tts_synthesizer
from app.config import settings
from dashscope.audio.tts_v2 import SpeechSynthesizer
# # 去除 @tool，并重命名以示区别
# async def process_text_to_speech(text: str) -> str:
#     """将文本转换为语音，直接返回 Base64 字符串，彻底告别磁盘读写
    
#     Returns:
#         str: 成功则返回 base64 字符串，失败则返回 "Error: ..."
#     """
#     try:
#         # 调用阿里云 TTS API 获取二进制音频流
#         # audio_data = tts_synthesizer.call(text)
#         synthesizer = create_tts_synthesizer()
#         audio_data = synthesizer.call(text)

#         if audio_data:
#             # 纯内存操作：将 bytes 直接转为 base64 字符串
#             return base64.b64encode(audio_data).decode('utf-8')
#         else:
#             return "Error: TTS 音频合成失败，API无返回数据"
            
#     except Exception as e:
#         return f"Error: {str(e)}"
    
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