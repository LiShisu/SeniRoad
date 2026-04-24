from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Numeric, Index
from sqlalchemy.orm import relationship
from app.database import Base

class FavoritePlace(Base):
    __tablename__ = "favorite_places"
    
    place_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='地点ID')
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment='所属老人ID')
    place_name = Column(String(100), nullable=False, comment='地点名称(如: 儿子家)')
    latitude = Column(Numeric(10, 8), nullable=False, comment='纬度')
    longitude = Column(Numeric(11, 8), nullable=False, comment='经度')
    address = Column(String(500), nullable=False, comment='详细地址')
    source_type = Column(Integer, default=1, comment='来源: 1-家属预设, 2-自动识别')
    is_active = Column(Integer, default=1, comment='是否激活')
    
    # 关联关系
    user = relationship("User", back_populates="favorite_places")
    
    # 索引
    __table_args__ = (
        Index('idx_user_source', 'user_id', 'source_type'),
    )
