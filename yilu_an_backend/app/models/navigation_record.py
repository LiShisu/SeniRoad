from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Numeric, Index
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class NavigationRecord(Base):
    __tablename__ = "navigation_records"
    
    record_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='记录ID')
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment='用户ID')
    start_time = Column(DateTime, nullable=False, comment='导航开始时间')
    end_time = Column(DateTime, nullable=True, comment='结束时间')
    origin_lat = Column(Numeric(10, 8), nullable=True, comment='起点纬度')
    origin_lng = Column(Numeric(11, 8), nullable=True, comment='起点经度')
    dest_lat = Column(Numeric(10, 8), nullable=False, comment='终点纬度')
    dest_lng = Column(Numeric(11, 8), nullable=False, comment='终点经度')
    dest_name = Column(String(100), nullable=True, comment='目的地名称')
    status = Column(Integer, default=1, comment='状态: 1-进行中, 2-完成, 3-取消')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    user = relationship("User", back_populates="navigation_records")
    
    # 索引
    __table_args__ = (
        Index('idx_user_start', 'user_id', 'start_time'),
    )
