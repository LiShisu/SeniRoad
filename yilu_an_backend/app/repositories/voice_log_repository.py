from sqlalchemy.orm import Session
from app.models.voice_log import VoiceLog
from typing import List, Optional
from datetime import datetime

class VoiceLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, log_id: int) -> Optional[VoiceLog]:
        return self.db.query(VoiceLog).filter(VoiceLog.log_id == log_id).first()

    def get_by_user_id(self, user_id: int, limit: int = 100) -> List[VoiceLog]:
        return self.db.query(VoiceLog).filter(
            VoiceLog.user_id == user_id
        ).order_by(VoiceLog.log_time.desc()).limit(limit).all()

    def get_by_record_id(self, record_id: int, limit: int = 100) -> List[VoiceLog]:
        return self.db.query(VoiceLog).filter(
            VoiceLog.record_id == record_id
        ).order_by(VoiceLog.log_time.desc()).limit(limit).all()

    def get_by_time_range(self, user_id: int, start_time: datetime, end_time: datetime) -> List[VoiceLog]:
        return self.db.query(VoiceLog).filter(
            VoiceLog.user_id == user_id,
            VoiceLog.log_time >= start_time,
            VoiceLog.log_time <= end_time
        ).order_by(VoiceLog.log_time.desc()).all()

    def create(self, voice_log: VoiceLog) -> VoiceLog:
        self.db.add(voice_log)
        self.db.commit()
        self.db.refresh(voice_log)
        return voice_log

    def update(self, voice_log: VoiceLog) -> VoiceLog:
        self.db.commit()
        self.db.refresh(voice_log)
        return voice_log

    def delete(self, voice_log: VoiceLog) -> None:
        self.db.delete(voice_log)
        self.db.commit()

    def delete_old_logs(self, user_id: int, before_date: datetime) -> int:
        deleted = self.db.query(VoiceLog).filter(
            VoiceLog.user_id == user_id,
            VoiceLog.log_time < before_date
        ).delete()
        self.db.commit()
        return deleted
