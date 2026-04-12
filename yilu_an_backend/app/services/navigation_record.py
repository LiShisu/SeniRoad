from sqlalchemy.orm import Session
from app.models.navigation_record import NavigationRecord
from app.schemas.navigation_record import NavigationRecordCreate, NavigationRecordUpdate, NavigationRecordResponse
from app.repositories.navigation_record_repository import NavigationRecordRepository
from typing import List, Optional
from datetime import datetime

class NavigationRecordService:
    def __init__(self, db: Session):
        self.navigation_record_repo = NavigationRecordRepository(db)
    
    def get_record_by_id(self, record_id: int) -> Optional[NavigationRecordResponse]:
        """根据ID获取导航记录"""
        record = self.navigation_record_repo.get_by_id(record_id)
        if record:
            return NavigationRecordResponse.model_validate(record)
        return None
    
    def get_records_by_user_id(self, user_id: int) -> List[NavigationRecordResponse]:
        """根据用户ID获取导航记录列表"""
        records = self.navigation_record_repo.get_by_user_id(user_id)
        return [NavigationRecordResponse.model_validate(record) for record in records]
    
    def get_active_records(self, user_id: int) -> List[NavigationRecordResponse]:
        """获取用户的进行中导航记录"""
        records = self.navigation_record_repo.get_active_records(user_id)
        return [NavigationRecordResponse.model_validate(record) for record in records]
    
    def get_completed_records(self, user_id: int, start_date: datetime = None, end_date: datetime = None) -> List[NavigationRecordResponse]:
        """获取用户的已完成导航记录"""
        records = self.navigation_record_repo.get_completed_records(user_id, start_date, end_date)
        return [NavigationRecordResponse.model_validate(record) for record in records]
    
    def get_records_by_status(self, user_id: int, status: int) -> List[NavigationRecordResponse]:
        """根据状态获取导航记录"""
        records = self.navigation_record_repo.get_records_by_status(user_id, status)
        return [NavigationRecordResponse.model_validate(record) for record in records]
    
    def create_record(self, record_data: NavigationRecordCreate) -> NavigationRecordResponse:
        """创建导航记录"""
        # 检查是否有进行中的导航记录
        active_records = self.navigation_record_repo.get_active_records(record_data.user_id)
        if active_records:
            # 可以选择结束之前的记录
            for record in active_records:
                record.status = 3  # 3-取消
                record.end_time = datetime.now()
                self.navigation_record_repo.update(record)
        
        # 创建导航记录实例
        record = NavigationRecord(
            user_id=record_data.user_id,
            start_time=record_data.start_time,
            end_time=record_data.end_time,
            origin_lat=record_data.origin_lat,
            origin_lng=record_data.origin_lng,
            dest_lat=record_data.dest_lat,
            dest_lng=record_data.dest_lng,
            dest_name=record_data.dest_name,
            status=record_data.status
        )
        
        # 保存记录
        created_record = self.navigation_record_repo.create(record)
        return NavigationRecordResponse.model_validate(created_record)
    
    def update_record(self, record_id: int, record_data: NavigationRecordUpdate) -> Optional[NavigationRecordResponse]:
        """更新导航记录"""
        record = self.navigation_record_repo.get_by_id(record_id)
        if not record:
            return None
        
        # 更新记录字段
        if record_data.end_time is not None:
            record.end_time = record_data.end_time
        if record_data.origin_lat is not None:
            record.origin_lat = record_data.origin_lat
        if record_data.origin_lng is not None:
            record.origin_lng = record_data.origin_lng
        if record_data.dest_name is not None:
            record.dest_name = record_data.dest_name
        if record_data.status is not None:
            record.status = record_data.status
            # 如果状态变为完成或取消，设置结束时间
            if record_data.status in [2, 3] and not record.end_time:
                record.end_time = datetime.now()
        
        # 保存更新
        updated_record = self.navigation_record_repo.update(record)
        return NavigationRecordResponse.model_validate(updated_record)
    
    def delete_record(self, record_id: int) -> bool:
        """删除导航记录"""
        record = self.navigation_record_repo.get_by_id(record_id)
        if not record:
            return False
        
        self.navigation_record_repo.delete(record)
        return True
    
    def complete_record(self, record_id: int) -> Optional[NavigationRecordResponse]:
        """完成导航记录"""
        record = self.navigation_record_repo.get_by_id(record_id)
        if not record:
            return None
        
        record.status = 2  # 2-完成
        record.end_time = datetime.now()
        updated_record = self.navigation_record_repo.update(record)
        return NavigationRecordResponse.model_validate(updated_record)
    
    def cancel_record(self, record_id: int) -> Optional[NavigationRecordResponse]:
        """取消导航记录"""
        record = self.navigation_record_repo.get_by_id(record_id)
        if not record:
            return None
        
        record.status = 3  # 3-取消
        record.end_time = datetime.now()
        updated_record = self.navigation_record_repo.update(record)
        return NavigationRecordResponse.model_validate(updated_record)
