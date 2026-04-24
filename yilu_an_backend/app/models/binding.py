from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime

class BindingStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Binding(Base):
    __tablename__ = "bindings"
    
    binding_id = Column(Integer, primary_key=True, index=True)
    elderly_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    family_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(Enum(BindingStatus), default=BindingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now)
    approved_at = Column(DateTime, nullable=True)
    
    elderly = relationship("User", foreign_keys=[elderly_id], back_populates="bindings_elderly")
    family = relationship("User", foreign_keys=[family_id], back_populates="bindings_family")
