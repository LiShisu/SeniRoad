from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Device(Base):
    __tablename__ = "devices"
    
    device_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='设备ID')
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment='关联的用户ID(老人)')
    device_token = Column(String(255), unique=True, nullable=False, comment='设备唯一标识/Token')
    device_model = Column(String(100), comment='设备型号')
    last_login_time = Column(DateTime, comment='最后登录时间')
    status = Column(Integer, default=1, comment='状态: 1-在线, 0-离线')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    user = relationship("User", backref="devices")
