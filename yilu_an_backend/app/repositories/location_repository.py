from sqlalchemy.orm import Session
from app.models.location import Location
from typing import List, Optional
from datetime import datetime

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, location_id: int) -> Optional[Location]:
        """根据ID获取位置"""
        return self.db.query(Location).filter(Location.id == location_id).first()
    
    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[Location]:
        """根据用户ID获取位置列表"""
        return self.db.query(Location).filter(Location.user_id == user_id).order_by(Location.created_at.desc()).limit(limit).all()
    
    def get_latest_by_user_id(self, user_id: int) -> Optional[Location]:
        """获取用户最新位置"""
        return self.db.query(Location).filter(Location.user_id == user_id).order_by(Location.created_at.desc()).first()
    
    def get_by_time_range(self, user_id: int, start_time: datetime, end_time: datetime) -> List[Location]:
        """根据时间范围获取位置"""
        return self.db.query(Location).filter(
            Location.user_id == user_id,
            Location.created_at >= start_time,
            Location.created_at <= end_time
        ).order_by(Location.created_at).all()
    
    def create(self, location: Location) -> Location:
        """创建位置记录"""
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location
    
    def bulk_create(self, locations: List[Location]) -> List[Location]:
        """批量创建位置记录"""
        self.db.add_all(locations)
        self.db.commit()
        for location in locations:
            self.db.refresh(location)
        return locations
    
    def delete_old_locations(self, user_id: int, before_time: datetime) -> int:
        """删除指定时间之前的位置记录"""
        deleted = self.db.query(Location).filter(
            Location.user_id == user_id,
            Location.created_at < before_time
        ).delete()
        self.db.commit()
        return deleted
