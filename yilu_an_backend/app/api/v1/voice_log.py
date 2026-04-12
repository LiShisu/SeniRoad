from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from app.schemas.voice_log import VoiceLogCreate, VoiceLogUpdate, VoiceLogResponse
from app.services.voice_log import VoiceLogService
from app.dependencies import get_voice_log_service, get_current_active_user
from app.models import User

router = APIRouter()

@router.post("/", response_model=VoiceLogResponse, status_code=status.HTTP_201_CREATED)
async def create_voice_log(
    log: VoiceLogCreate,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """创建语音日志"""
    return voice_log_service.create_log(log)

@router.get("/", response_model=List[VoiceLogResponse])
async def get_voice_logs(
    user_id: int,
    limit: int = 100,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的语音日志列表
    
    - user_id: 用户ID
    - limit: 返回日志数量限制（默认100）
    """
    return voice_log_service.get_logs_by_user_id(user_id, limit)

@router.get("/device/{device_id}", response_model=List[VoiceLogResponse])
async def get_voice_logs_by_device(
    device_id: int,
    limit: int = 100,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据设备ID获取语音日志列表
    
    - device_id: 设备ID
    - limit: 返回日志数量限制（默认100）
    """
    return voice_log_service.get_logs_by_device_id(device_id, limit)

@router.get("/time-range/{user_id}", response_model=List[VoiceLogResponse])
async def get_voice_logs_by_time_range(
    user_id: int,
    start_time: datetime,
    end_time: datetime,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据时间范围获取语音日志
    
    - user_id: 用户ID
    - start_time: 开始时间
    - end_time: 结束时间
    """
    return voice_log_service.get_logs_by_time_range(user_id, start_time, end_time)

@router.get("/recent/{user_id}", response_model=List[VoiceLogResponse])
async def get_recent_voice_logs(
    user_id: int,
    hours: int = 24,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取最近几小时的语音日志
    
    - user_id: 用户ID
    - hours: 最近几小时（默认24）
    """
    return voice_log_service.get_recent_logs(user_id, hours)

@router.get("/{log_id}", response_model=VoiceLogResponse)
async def get_voice_log(
    log_id: int,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取语音日志"""
    log = voice_log_service.get_log_by_id(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="语音日志不存在"
        )
    return log

@router.put("/{log_id}", response_model=VoiceLogResponse)
async def update_voice_log(
    log_id: int,
    log: VoiceLogUpdate,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """更新语音日志"""
    updated_log = voice_log_service.update_log(log_id, log)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="语音日志不存在"
        )
    return updated_log

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voice_log(
    log_id: int,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """删除语音日志"""
    success = voice_log_service.delete_log(log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="语音日志不存在"
        )

@router.delete("/user/{user_id}/old", response_model=dict)
async def delete_old_voice_logs(
    user_id: int,
    days: int = 30,
    voice_log_service: VoiceLogService = Depends(get_voice_log_service),
    current_user: User = Depends(get_current_active_user)
):
    """删除指定天数之前的语音日志
    
    - user_id: 用户ID
    - days: 天数（默认30）
    
    Returns:
        dict: 包含删除数量的响应
    """
    deleted_count = voice_log_service.delete_old_logs(user_id, days)
    return {"deleted_count": deleted_count}
