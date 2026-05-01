from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class VoiceLogBase(BaseModel):
    user_id: int = Field(..., description="用户ID")
    record_id: Optional[int] = Field(None, description="关联导航记录ID")
    audio_url: Optional[str] = Field(None, max_length=255, description="语音文件存储路径")
    asr_text: Optional[str] = Field(None, description="语音识别转文本")
    intent_json: Optional[Dict[str, Any]] = Field(None, description="AI解析的意图结构化数据")
    response_text: Optional[str] = Field(None, description="系统回复文本")
    log_time: datetime = Field(..., description="日志时间")

class VoiceLogCreate(VoiceLogBase):
    pass

class VoiceLogUpdate(BaseModel):
    record_id: Optional[int] = Field(None, description="关联导航记录ID")
    audio_url: Optional[str] = Field(None, max_length=255, description="语音文件存储路径")
    asr_text: Optional[str] = Field(None, description="语音识别转文本")
    intent_json: Optional[Dict[str, Any]] = Field(None, description="AI解析的意图结构化数据")
    response_text: Optional[str] = Field(None, description="系统回复文本")

class VoiceLogResponse(VoiceLogBase):
    log_id: int
    created_at: datetime

    class Config:
        from_attributes = True
