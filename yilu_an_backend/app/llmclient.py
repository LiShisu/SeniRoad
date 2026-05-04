from langchain_openai import ChatOpenAI
from dashscope.audio.tts_v2 import SpeechSynthesizer
from dashscope.audio.asr import Recognition
import dashscope
from app.config import settings

# 初始化 DashScope 配置
def _setup_dashscope():
    dashscope.api_key = settings.DASHSCOPE_API_KEY
    dashscope.base_http_api_url = settings.DASHSCOPE_BASE_URL
    dashscope.base_websocket_api_url = settings.DASHSCOPE_BASE_URL.replace('https://', 'wss://').replace('http://', 'wss://')

_setup_dashscope()

# TTS Synthesizer
tts_synthesizer = SpeechSynthesizer(
    model=settings.DASHSCOPE_TTS_MODEL,
    voice=settings.DASHSCOPE_TTS_VOICE
)

# ASR Recognition
def create_asr_recognizer(file_urls: list):
    return Recognition(
        model=settings.DASHSCOPE_ASR_MODEL,
        file_urls=file_urls
    )

# Text model
text_llm = ChatOpenAI(
    model=settings.DASHSCOPE_TEXT_MODEL,
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.DASHSCOPE_BASE_URL,
    temperature=0,
)