from fastapi import UploadFile
from app.config import settings
from app.llmclient import call_asr
import tempfile
import asyncio
import os

async def process_speech_to_text(audio_file: UploadFile) -> str:
    """将前端上传的音频文件转换为文本"""
    """直接传入本地文件路径到Qwen3-ASR-Flash模型"""
    temp_file_path = None
    try:
        os.makedirs(settings.TEMP_DIR, exist_ok=True)

        USE_LOCAL_TEST_FILE = True  # 测试完毕准备上线时，把这里改成 False 即可！
        if USE_LOCAL_TEST_FILE:
            temp_file_path = os.path.join(settings.TEMP_DIR, "campus.wav")
            print(f"正在使用本地测试文件: {temp_file_path}")
        else:
            # 异步读取文件内容
            content = await audio_file.read()
            
            with tempfile.NamedTemporaryFile(dir=settings.TEMP_DIR, delete=False, suffix=".wav") as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
        
        if not os.path.exists(temp_file_path):
            return f"Error: 音频文件不存在 - {temp_file_path}"
        
        def _call_asr():
            return call_asr(temp_file_path)
        
        result = await asyncio.to_thread(_call_asr)
        
        if result.status_code == 200:
            if result.output and 'choices' in result.output:
                message = result.output['choices'][0]['message']
                if 'content' in message:
                    content_list = message['content']
                    if isinstance(content_list, list) and len(content_list) > 0:
                        asr_text = content_list[0].get('text', '')
                        if asr_text:
                            return asr_text
                        return "ASR Error: 识别成功，但未提取到有效文本"
                    elif isinstance(message['content'], str):
                        return message['content']
            return "ASR Error: 识别成功，但未提取到有效文本"
        else:
            return f"Error: ASR识别失败 - {result.message if result.message else '未知错误'}"

    except Exception as e:
        return f"Error: 内部执行异常 - {str(e)}"
    # TODO: 处理临时文件删除逻辑
    # finally:
    #     # ==========================================
    #     # 5. 打扫战场：无论如何，把前端上传产生的临时垃圾文件删掉
    #     # ==========================================
    #     if temp_file_path and os.path.exists(temp_file_path):
    #         try:
    #             os.unlink(temp_file_path)
    #         except Exception as e:
    #             pass