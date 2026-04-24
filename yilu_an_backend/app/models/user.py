from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Date
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime

class UserRole(enum.Enum):
    ELDERLY = "elderly"
    FAMILY = "family"

# TODO: 完善用户模型，添加性别、生日字段
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    nickname = Column(String(50), nullable=True)

    # 微信小程序相关字段
    openid = Column(String(255), unique=True, index=True, nullable=True)
    session_key = Column(String(255), nullable=True)

    role = Column(Enum(UserRole), nullable=False)
    gender = Column(Integer, nullable=True, default=9)
    birthday = Column(Date, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    """
    1.relationship 函数 ：
    - 用于定义模型之间的关联关系
    - 第一个参数是关联的目标模型名称
    - back_populates 参数指定目标模型中对应的关系字段
    
    2.普通关系 ：
    - User 模型可以有多个 Location、FavoritePlace、NavigationRecord 和 VoiceLog
    - 这些模型中应该有对应的 user 字段指向 User
    
    3.自引用关系 （bindings_elderly 和 bindings_family）：
    - 这是一种特殊的关系，因为 Binding 模型同时引用了两个 User （老人和家属）
    - 需要使用 foreign_keys 参数明确指定外键，避免歧义
    - bindings_elderly ：当前用户作为老人的绑定关系
    - bindings_family ：当前用户作为家属的绑定关系
    """
    # 定义与 Location 模型的关系
    locations = relationship("Location", back_populates="user")
    # 定义与 FavoritePlace 模型的关系
    favorite_places = relationship("FavoritePlace", back_populates="user")
    # 定义与 NavigationRecord 模型的关系
    navigation_records = relationship("NavigationRecord", back_populates="user")
    # 定义与 VoiceLog 模型的关系
    voice_logs = relationship("VoiceLog", back_populates="user")
    # 定义与 Binding 模型的关系（作为老人
    bindings_elderly = relationship("Binding", foreign_keys="Binding.elderly_id", back_populates="elderly")
    # 定义与 Binding 模型的关系（作为家庭成员）
    bindings_family = relationship("Binding", foreign_keys="Binding.family_id", back_populates="family")
