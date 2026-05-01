from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, BigInteger, Numeric, Index
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Location(Base):
    __tablename__ = "locations"

    location_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    record_id = Column(BigInteger, ForeignKey("navigation_records.record_id", ondelete="SET NULL"), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    address = Column(String(255), nullable=True)
    accuracy = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_locations_user_time", "user_id", "created_at"),
        Index("idx_locations_record", "record_id"),
    )

    user = relationship("User", back_populates="locations")
    navigation_record = relationship("NavigationRecord", back_populates="locations")
