from sqlalchemy.orm import Session
from app.models.voice_log import VoiceLog
from typing import List, Optional
from datetime import datetime

class VoiceLogRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, log_id: int) -> Optional[VoiceLog]:
        """根据ID获取语音日志"""
        return self.db.query(VoiceLog).filter(VoiceLog.log_id == log_id).first()
    
    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[VoiceLog]:
        """根据用户ID获取语音日志列表"""
        return self.db.query(VoiceLog).filter(
            VoiceLog.user_id == user_id
        ).order_by(VoiceLog.log_time.desc()).limit(limit).all()
    
    def get_by_device_id(self, device_id: int, limit: int = 100) -> List[VoiceLog]:
        """根据设备ID获取语音日志列表"""
        return self.db.query(VoiceLog).filter(
            VoiceLog.device_id == device_id
        ).order_by(VoiceLog.log_time.desc()).limit(limit).all()
    
    def get_by_time_range(self, user_id: int, start_time: datetime, end_time: datetime) -> List[VoiceLog]:
        """根据时间范围获取语音日志"""
        return self.db.query(VoiceLog).filter(
            VoiceLog.user_id == user_id,
            VoiceLog.log_time >= start_time,
            VoiceLog.log_time <= end_time
        ).order_by(VoiceLog.log_time.desc()).all()
    
    def create(self, voice_log: VoiceLog) -> VoiceLog:
        """创建语音日志"""
        self.db.add(voice_log)
        self.db.commit()
        self.db.refresh(voice_log)
        return voice_log
    
    def update(self, voice_log: VoiceLog) -> VoiceLog:
        """更新语音日志"""
        self.db.commit()
        self.db.refresh(voice_log)
        return voice_log
    
    def delete(self, voice_log: VoiceLog) -> None:
        """删除语音日志"""
        self.db.delete(voice_log)
        self.db.commit()
    
    def delete_old_logs(self, user_id: int, before_date: datetime) -> int:
        """删除指定日期之前的语音日志"""
        deleted = self.db.query(VoiceLog).filter(
            VoiceLog.user_id == user_id,
            VoiceLog.log_time < before_date
        ).delete()
        self.db.commit()
        return deleted
