from langchain_openai import ChatOpenAI
from app.config import settings

# 初始化模型
# Voice model
voice_llm = ChatOpenAI(
    model=settings.VOICE_MODEL,  # 指定 Omni 系列模型名称
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    temperature=0,             # 设置为0以获得更稳定的工具调用结果
)

# Text model
text_llm = ChatOpenAI(
    model=settings.TEXT_MODEL,  # 指定 DeepSeek V3.2 模型名称
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    temperature=0,             # 设置为0以获得更稳定的工具调用结果
)