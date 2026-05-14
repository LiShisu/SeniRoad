from dashscope.audio.tts_v2 import SpeechSynthesizer
from langchain_openai import ChatOpenAI
from dashscope.audio.asr import Recognition
import dashscope
import base64
# from app.config import settings
def _setup_dashscope():
    dashscope.api_key = "sk-e0272e80d6f8482da0e3ed27c73b395d"
    # dashscope.base_http_api_url = settings.DASHSCOPE_BASE_URL
_setup_dashscope()
file_path = "C:\\SeniRoad\\yilu_an_backend\\temp\\回家.wav"
# file_path = "C:\\SeniRoad\\yilu_an_backend\\app\\agent\\tools\\output_sync.wav"
print(f"正在读取文件: {file_path}")
# 初始化合成器
messages = [
    {"role": "user", "content": [{"audio": file_path}]}
]
result = dashscope.MultiModalConversation.call(
        model="qwen3-asr-flash",
        format='wav',
        asr_options={
        # "language": "zh", # 可选，若已知音频的语种，可通过该参数指定待识别语种，以提升识别准确率
        "enable_itn":False
    },
        result_format="message",
        messages=messages,
    )
if result.status_code == 200:
    if result:
        content_list = result.output['choices'][0]['message']['content']
        asr_text = content_list[0]['text']  # 提取结果
        print(f"🎉 识别成功！结果是: {asr_text}")
    else:
        print("🤔 识别成功，但音频里似乎没有说话的声音。")
else:
    print(f"❌ Error: ASR识别失败 - {result.message}")