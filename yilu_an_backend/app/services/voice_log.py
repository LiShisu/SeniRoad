from sqlalchemy.orm import Session
from app.models.voice_log import VoiceLog
from app.schemas.voice_log import VoiceLogCreate, VoiceLogUpdate, VoiceLogResponse
from app.repositories.voice_log_repository import VoiceLogRepository
from typing import List, Optional
from datetime import datetime, timedelta

class VoiceLogService:
    def __init__(self, db: Session):
        self.voice_log_repo = VoiceLogRepository(db)

    def get_log_by_id(self, log_id: int) -> Optional[VoiceLogResponse]:
        log = self.voice_log_repo.get_by_id(log_id)
        if log:
            return VoiceLogResponse.model_validate(log)
        return None

    def get_logs_by_user_id(self, user_id: int, limit: int = 100) -> List[VoiceLogResponse]:
        logs = self.voice_log_repo.get_by_user_id(user_id, limit)
        return [VoiceLogResponse.model_validate(log) for log in logs]

    def get_logs_by_record_id(self, record_id: int, limit: int = 100) -> List[VoiceLogResponse]:
        logs = self.voice_log_repo.get_by_record_id(record_id, limit)
        return [VoiceLogResponse.model_validate(log) for log in logs]

    def get_logs_by_time_range(self, user_id: int, start_time: datetime, end_time: datetime) -> List[VoiceLogResponse]:
        logs = self.voice_log_repo.get_by_time_range(user_id, start_time, end_time)
        return [VoiceLogResponse.model_validate(log) for log in logs]

    def create_log(self, log_data: VoiceLogCreate) -> VoiceLogResponse:
        log = VoiceLog(
            user_id=log_data.user_id,
            record_id=log_data.record_id,
            audio_url=log_data.audio_url,
            asr_text=log_data.asr_text,
            intent_json=log_data.intent_json,
            response_text=log_data.response_text,
            log_time=log_data.log_time
        )

        created_log = self.voice_log_repo.create(log)
        return VoiceLogResponse.model_validate(created_log)

    def update_log(self, log_id: int, log_data: VoiceLogUpdate) -> Optional[VoiceLogResponse]:
        log = self.voice_log_repo.get_by_id(log_id)
        if not log:
            return None

        if log_data.record_id is not None:
            log.record_id = log_data.record_id
        if log_data.audio_url is not None:
            log.audio_url = log_data.audio_url
        if log_data.asr_text is not None:
            log.asr_text = log_data.asr_text
        if log_data.intent_json is not None:
            log.intent_json = log_data.intent_json
        if log_data.response_text is not None:
            log.response_text = log_data.response_text

        updated_log = self.voice_log_repo.update(log)
        return VoiceLogResponse.model_validate(updated_log)

    def delete_log(self, log_id: int) -> bool:
        log = self.voice_log_repo.get_by_id(log_id)
        if not log:
            return False

        self.voice_log_repo.delete(log)
        return True

    def delete_old_logs(self, user_id: int, days: int = 30) -> int:
        before_date = datetime.now() - timedelta(days=days)
        return self.voice_log_repo.delete_old_logs(user_id, before_date)

    def get_recent_logs(self, user_id: int, hours: int = 24) -> List[VoiceLogResponse]:
        start_time = datetime.now() - timedelta(hours=hours)
        end_time = datetime.now()
        logs = self.voice_log_repo.get_by_time_range(user_id, start_time, end_time)
        return [VoiceLogResponse.model_validate(log) for log in logs]
