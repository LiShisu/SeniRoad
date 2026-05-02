from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(BigInteger, primary_key=True, autoincrement=True)
    tag_name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=True)
    icon = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("tag_name", name="uq_tags_tag_name"),
        Index("idx_tags_active", "is_active"),
    )

    favorite_places = relationship("FavoritePlace", back_populates="tag")
