from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Numeric, Index
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class NavigationRecord(Base):
    __tablename__ = "navigation_records"

    record_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    origin_lat = Column(Numeric(10, 8), nullable=True)
    origin_lng = Column(Numeric(11, 8), nullable=True)
    dest_lat = Column(Numeric(10, 8), nullable=False)
    dest_lng = Column(Numeric(11, 8), nullable=False)
    dest_name = Column(String(100), nullable=True)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_nav_user_start", "user_id", "start_time"),
        Index("idx_nav_status", "status"),
    )

    user = relationship("User", back_populates="navigation_records")
    locations = relationship("Location", back_populates="navigation_record")
    voice_logs = relationship("VoiceLog", back_populates="navigation_record")
