from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Date, BigInteger, SmallInteger, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime, timezone

class UserRole(enum.Enum):
    ELDERLY = "elderly"
    FAMILY = "family"

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False)
    nickname = Column(String(50), nullable=True)
    openid = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    gender = Column(SmallInteger, nullable=True, default=9)
    birthday = Column(Date, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("gender IN (0, 1, 9)", name="ck_users_gender"),
        UniqueConstraint("openid", "role", name="uq_users_openid_role"),
    )

    locations = relationship("Location", back_populates="user")
    favorite_places = relationship("FavoritePlace", back_populates="user")
    navigation_records = relationship("NavigationRecord", back_populates="user")
    voice_logs = relationship("VoiceLog", back_populates="user")
    bindings_elderly = relationship("Binding", foreign_keys="Binding.elderly_id", back_populates="elderly")
    bindings_family = relationship("Binding", foreign_keys="Binding.family_id", back_populates="family")
