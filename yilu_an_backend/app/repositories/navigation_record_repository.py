from sqlalchemy.orm import Session
from app.models.navigation_record import NavigationRecord
from typing import List, Optional
from datetime import datetime

class NavigationRecordRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, record_id: int) -> Optional[NavigationRecord]:
        """根据ID获取导航记录"""
        return self.db.query(NavigationRecord).filter(NavigationRecord.record_id == record_id).first()
    
    def get_by_user_id(self, user_id: int) -> List[NavigationRecord]:
        """根据用户ID获取导航记录列表"""
        return self.db.query(NavigationRecord).filter(
            NavigationRecord.user_id == user_id
        ).order_by(NavigationRecord.start_time.desc()).all()
    
    def get_active_records(self, user_id: int) -> List[NavigationRecord]:
        """获取用户的进行中导航记录"""
        return self.db.query(NavigationRecord).filter(
            NavigationRecord.user_id == user_id,
            NavigationRecord.status == 1  # 1-进行中
        ).all()
    
    def get_completed_records(self, user_id: int, start_date: datetime = None, end_date: datetime = None) -> List[NavigationRecord]:
        """获取用户的已完成导航记录"""
        query = self.db.query(NavigationRecord).filter(
            NavigationRecord.user_id == user_id,
            NavigationRecord.status == 2  # 2-完成
        )
        
        if start_date:
            query = query.filter(NavigationRecord.start_time >= start_date)
        if end_date:
            query = query.filter(NavigationRecord.start_time <= end_date)
        
        return query.order_by(NavigationRecord.start_time.desc()).all()
    
    def get_records_by_status(self, user_id: int, status: int) -> List[NavigationRecord]:
        """根据状态获取导航记录"""
        return self.db.query(NavigationRecord).filter(
            NavigationRecord.user_id == user_id,
            NavigationRecord.status == status
        ).order_by(NavigationRecord.start_time.desc()).all()
    
    def create(self, navigation_record: NavigationRecord) -> NavigationRecord:
        """创建导航记录"""
        self.db.add(navigation_record)
        self.db.commit()
        self.db.refresh(navigation_record)
        return navigation_record
    
    def update(self, navigation_record: NavigationRecord) -> NavigationRecord:
        """更新导航记录"""
        self.db.commit()
        self.db.refresh(navigation_record)
        return navigation_record
    
    def delete(self, navigation_record: NavigationRecord) -> None:
        """删除导航记录"""
        self.db.delete(navigation_record)
        self.db.commit()
