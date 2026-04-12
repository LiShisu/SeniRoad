from sqlalchemy.orm import Session
from app.models.destination import Destination
from typing import List, Optional

class DestinationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, destination_id: int) -> Optional[Destination]:
        """根据ID获取目的地"""
        return self.db.query(Destination).filter(Destination.id == destination_id).first()
    
    def get_by_user_id(self, user_id: int) -> List[Destination]:
        """根据用户ID获取目的地列表"""
        return self.db.query(Destination).filter(Destination.user_id == user_id).all()
    
    def get_common_destinations(self, user_id: int) -> List[Destination]:
        """获取用户的常用目的地"""
        return self.db.query(Destination).filter(
            Destination.user_id == user_id,
            Destination.is_common == True
        ).all()
    
    def create(self, destination: Destination) -> Destination:
        """创建目的地"""
        self.db.add(destination)
        self.db.commit()
        self.db.refresh(destination)
        return destination
    
    def update(self, destination: Destination) -> Destination:
        """更新目的地"""
        self.db.commit()
        self.db.refresh(destination)
        return destination
    
    def delete(self, destination: Destination) -> None:
        """删除目的地"""
        self.db.delete(destination)
        self.db.commit()
    
    def exists_by_name(self, user_id: int, name: str) -> bool:
        """检查用户是否已存在同名目的地"""
        return self.db.query(Destination).filter(
            Destination.user_id == user_id,
            Destination.name == name
        ).first() is not None
