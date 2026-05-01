from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime, timezone

class BindingStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Binding(Base):
    __tablename__ = "bindings"

    binding_id = Column(BigInteger, primary_key=True, autoincrement=True)
    elderly_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    family_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(BindingStatus), nullable=False, default=BindingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    approved_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("elderly_id", "family_id", name="uq_bindings_elderly_family"),
    )

    elderly = relationship("User", foreign_keys=[elderly_id], back_populates="bindings_elderly")
    family = relationship("User", foreign_keys=[family_id], back_populates="bindings_family")
