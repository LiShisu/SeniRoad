from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class VoiceLog(Base):
    __tablename__ = "voice_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    record_id = Column(BigInteger, ForeignKey("navigation_records.record_id", ondelete="SET NULL"), nullable=True)
    audio_url = Column(String(255), nullable=True)
    asr_text = Column(Text, nullable=True)
    intent_json = Column(JSONB, nullable=True)
    response_text = Column(Text, nullable=True)
    log_time = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_voice_user_time", "user_id", "log_time"),
        Index("idx_voice_record", "record_id"),
        Index("idx_voice_intent", "intent_json", postgresql_using="gin"),
    )

    user = relationship("User", back_populates="voice_logs")
    navigation_record = relationship("NavigationRecord", back_populates="voice_logs")
