from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class VoiceLog(Base):
    __tablename__ = "voice_logs"
    
    log_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment='用户ID')

    audio_url = Column(String(255), nullable=True, comment='语音文件存储路径')
    asr_text = Column(Text, nullable=True, comment='语音识别转文本')
    intent_json = Column(Text, nullable=True, comment='AI解析的意图结构化数据')
    response_text = Column(Text, nullable=True, comment='系统回复文本')
    log_time = Column(DateTime, default=datetime.now, comment='日志时间')
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    user = relationship("User", back_populates="voice_logs")


