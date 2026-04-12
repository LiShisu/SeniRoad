"""
这是示例模型，请忽略它的实现
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime

class UserRole(enum.Enum):
    ELDERLY = "elderly"
    FAMILY = "family"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    nickname = Column(String(50))
    password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), nullable=False)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    """
    1.relationship 函数 ：
    - 用于定义模型之间的关联关系
    - 第一个参数是关联的目标模型名称
    - back_populates 参数指定目标模型中对应的关系字段
    
    2.普通关系 （locations 和 destinations）：
    - User 模型可以有多个 Location 和 Destination
    - Location 和 Destination 模型中应该有对应的 user 字段指向 User
    
    3.自引用关系 （bindings_elderly 和 bindings_family）：
    - 这是一种特殊的关系，因为 Binding 模型同时引用了两个 User （老人和家属）
    - 需要使用 foreign_keys 参数明确指定外键，避免歧义
    - bindings_elderly ：当前用户作为老人的绑定关系
    - bindings_family ：当前用户作为家属的绑定关系
    """
    # 定义与 Location 模型的关系
    locations = relationship("Location", back_populates="user")
    # 定义与 Destination 模型的关系
    destinations = relationship("Destination", back_populates="user")
    # 定义与 Binding 模型的关系（作为老人
    bindings_elderly = relationship("Binding", foreign_keys="Binding.elderly_id", back_populates="elderly")
    # 定义与 Binding 模型的关系（作为家庭成员）
    bindings_family = relationship("Binding", foreign_keys="Binding.family_id", back_populates="family")
