from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class VoiceLog(Base):
    __tablename__ = "voice_logs"
    
    log_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='用户ID')
    device_id = Column(BigInteger, ForeignKey("devices.device_id", ondelete="SET NULL"), comment='设备ID')
    audio_url = Column(String(255), comment='语音文件存储路径')
    asr_text = Column(Text, comment='语音识别转文本')
    intent_json = Column(Text, comment='AI解析的意图结构化数据')
    response_text = Column(Text, comment='系统回复文本')
    log_time = Column(DateTime, default=datetime.now, comment='日志时间')
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联关系
    user = relationship("User", backref="voice_logs")
    device = relationship("Device", backref="voice_logs")
