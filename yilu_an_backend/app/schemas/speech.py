from pydantic import BaseModel, Field

class TextToSpeechRequest(BaseModel):
    """文本转语音请求"""
    text: str = Field(..., description="需要转换的文本内容", min_length=1, max_length=500)

class TextToSpeechResponse(BaseModel):
    """文本转语音响应"""
    status: str = "success"
    audio_url: str = ""
    audio_data: str = ""
