from dashscope.audio.tts_v2 import SpeechSynthesizer
from langchain_openai import ChatOpenAI
from dashscope.audio.tts_v2 import SpeechSynthesizer
from dashscope.audio.asr import Recognition
import dashscope
import base64
# from app.config import settings
def _setup_dashscope():
    dashscope.api_key = "sk-e0272e80d6f8482da0e3ed27c73b395d"
    # dashscope.base_http_api_url = settings.DASHSCOPE_BASE_URL
_setup_dashscope()
# 初始化合成器
synthesizer = SpeechSynthesizer(model="cosyvoice-v2", voice="longxiaochun_v2")
 
# 同步调用：提交文本，获取二进制音频
audio_data = synthesizer.call("今天天气很好")  # 文本长度需 ≤2000 字符
audio_base64 = base64.b64encode(audio_data).decode("utf-8")
print("前端可用 Base64 音频：", audio_base64[:50], "...")
# 保存音频到本地
with open("output_sync.mp3", "wb") as f:
    f.write(audio_data)
 
# 打印请求指标
print(f"[Metric] 请求ID: {synthesizer.get_last_request_id()}, 首包延迟: {synthesizer.get_first_package_delay()}毫秒")