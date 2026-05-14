# from pydantic import BaseModel, Field

# class TextToSpeechRequest(BaseModel):
#     """文本转语音请求"""
#     text: str = Field(..., description="需要转换的文本内容", min_length=1, max_length=500)

# class TextToSpeechResponse(BaseModel):
#     """文本转语音响应"""
#     status: str = "success"
#     audio_url: str = ""
#     audio_data: str = ""

from pydantic import BaseModel, Field

# ---------------- 请求表述 ----------------
class SpeechSynthesisRequest(BaseModel):
    """文本转语音请求 (原 TextToSpeechRequest)"""
    text: str = Field(..., description="需要转换的文本内容", min_length=1, max_length=500)

# ---------------- 响应表述 ----------------
class SpeechSynthesisResponse(BaseModel):
    """文本转语音响应 (去除没用的 url 字段，专注 base64)"""
    audio_data: str = Field(..., description="Base64 编码的音频数据")
    audio_type: str = Field(default="audio/mpeg", description="音频 MIME 类型")

class SpeechRecognitionResponse(BaseModel):
    """语音转文本响应"""
    text: str = Field(..., description="识别出的文本")