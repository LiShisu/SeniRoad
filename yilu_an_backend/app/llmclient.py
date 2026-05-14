from langchain_openai import ChatOpenAI
from dashscope.audio.tts_v2 import SpeechSynthesizer
from dashscope.audio.asr import Recognition
import dashscope
from app.config import settings

# 初始化 DashScope 配置
def _setup_dashscope():
    if settings.DASHSCOPE_API_KEY:
        dashscope.api_key = settings.DASHSCOPE_API_KEY
    else:
        # 使用默认测试API密钥
        dashscope.api_key = "sk-e0272e80d6f8482da0e3ed27c73b395d"
    # dashscope.base_http_api_url = settings.DASHSCOPE_BASE_URL
    # dashscope.base_websocket_api_url = settings.DASHSCOPE_BASE_URL.replace('https://', 'wss://').replace('http://', 'wss://')

_setup_dashscope()

# TTS Synthesizer
# tts_synthesizer = SpeechSynthesizer(
#     model=settings.DASHSCOPE_TTS_MODEL,
#     voice=settings.DASHSCOPE_TTS_VOICE,
# )
def create_tts_synthesizer():
    return SpeechSynthesizer(
        model=settings.DASHSCOPE_TTS_MODEL,
        voice=settings.DASHSCOPE_TTS_VOICE
    )
    
# ASR Recognition (使用 MultiModalConversation API)
def call_asr(audio_data_uri):
    """
    使用 DashScope Qwen3-ASR-Flash 模型进行语音识别
    
    参数:
        audio_data_uri: Base64 编码的音频数据 URI，格式为 data:audio/wav;base64,...
    
    返回:
        ASR 识别结果
    """
    return dashscope.MultiModalConversation.call(
        model=settings.DASHSCOPE_ASR_MODEL,
        messages=[{"role": "user", "content": [{"audio": audio_data_uri}]}],
        result_format="message"
    )

# Text model
text_llm = ChatOpenAI(
    model=settings.DASHSCOPE_TEXT_MODEL,
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
    temperature=0,
)