from fastapi import UploadFile
from app.config import settings
import tempfile
import asyncio
import os
import dashscope

async def process_speech_to_text(audio_file: UploadFile) -> str:
    """将前端上传的音频文件转换为文本"""
    """保留了处理前端上传文件的逻辑，但实际上使用的是自己移动设备录音文件"""
    temp_file_path = None
    try:
        os.makedirs(settings.TEMP_DIR, exist_ok=True)

        # 异步读取文件内容
        content = await audio_file.read()
        
        with tempfile.NamedTemporaryFile(dir=settings.TEMP_DIR, delete=False, suffix=".wav") as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        USE_LOCAL_TEST_FILE = True  # 测试完毕准备上线时，把这里改成 False 即可！
        if USE_LOCAL_TEST_FILE:
            target_file_path = "C:\\SeniRoad\\yilu_an_backend\\temp\\老二家.wav"
            print(f"正在使用本地测试文件: {target_file_path}")
        else:
            target_file_path = temp_file_path
        messages = [
            {"role": "user", "content": [{"audio": target_file_path}]}
        ]
        def _call_multimodal_asr():
            return dashscope.MultiModalConversation.call(
                model="qwen3-asr-flash",
                format='wav',
                asr_options={"enable_itn": False},
                result_format="message",
                messages=messages,
            )
        result = await asyncio.to_thread(_call_multimodal_asr)
        if result.status_code == 200:
            if result.output and 'choices' in result.output:
                content_list = result.output['choices'][0]['message']['content']
                asr_text = content_list[0]['text']
                return asr_text
            else:
                return "ASR Error: 识别成功，但未提取到有效文本"
        else:
            return f"Error: ASR识别失败 - {result.message}"

    except Exception as e:
        return f"Error: 内部执行异常 - {str(e)}"
    # finally:
    #     # ==========================================
    #     # 5. 打扫战场：无论如何，把前端上传产生的临时垃圾文件删掉
    #     # ==========================================
    #     if temp_file_path and os.path.exists(temp_file_path):
    #         try:
    #             os.unlink(temp_file_path)
    #         except Exception as e:
    #             pass