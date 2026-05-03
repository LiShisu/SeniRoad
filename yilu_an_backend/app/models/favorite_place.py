from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Numeric, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class FavoritePlace(Base):
    __tablename__ = "favorite_places"

    place_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(BigInteger, ForeignKey("tags.tag_id", ondelete="SET NULL"), nullable=True)
    place_name = Column(String(100), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    address = Column(String(500), nullable=False)
    source_type = Column(Integer, nullable=False, default=1)  # 1-家属预设, 2-自动识别
    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("idx_fav_user_source", "user_id", "source_type"),
        UniqueConstraint("user_id", "place_name", name="uq_fav_user_place"),
    )

    user = relationship("User", back_populates="favorite_places")
    tag = relationship("Tag", back_populates="favorite_places")

