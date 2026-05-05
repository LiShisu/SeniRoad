from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from app.schemas.navigation_record import NavigationRecordCreate, NavigationRecordUpdate, NavigationRecordResponse
from app.services.navigation_record import NavigationRecordService
from app.dependencies import get_navigation_record_service, get_current_active_user
from app.models import User

router = APIRouter()

@router.post("/", response_model=NavigationRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_navigation_record(
    record: NavigationRecordCreate,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    if record.user_id is None:
        record.user_id = current_user.user_id
    return navigation_record_service.create_record(record)

@router.get("/", response_model=List[NavigationRecordResponse])
async def get_navigation_records(
    user_id: int = None,
    status: int = None,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取导航记录列表
    
    - user_id: 用户ID
    - status: 状态（可选，1-进行中, 2-完成, 3-取消）
    """
    if user_id is None:
        user_id = current_user.user_id
    if status:
        return navigation_record_service.get_records_by_status(user_id, status)
    return navigation_record_service.get_records_by_user_id(user_id)

@router.get("/user/{user_id}/active", response_model=List[NavigationRecordResponse])
async def get_active_navigation_records(
    user_id: int = None,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    if user_id is None:
        user_id = current_user.user_id
    return navigation_record_service.get_active_records(user_id)

@router.get("/user/{user_id}/completed", response_model=List[NavigationRecordResponse])
async def get_completed_navigation_records(
    user_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的已完成导航记录
    
    - start_date: 开始日期（可选）
    - end_date: 结束日期（可选）
    """
    if user_id is None:
        user_id = current_user.user_id
    return navigation_record_service.get_completed_records(user_id, start_date, end_date)

@router.get("/{record_id}", response_model=NavigationRecordResponse)
async def get_navigation_record(
    record_id: int,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取导航记录"""
    record = navigation_record_service.get_record_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导航记录不存在"
        )
    return record

@router.put("/{record_id}", response_model=NavigationRecordResponse)
async def update_navigation_record(
    record_id: int,
    record: NavigationRecordUpdate,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """更新导航记录"""
    updated_record = navigation_record_service.update_record(record_id, record)
    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导航记录不存在"
        )
    return updated_record

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_navigation_record(
    record_id: int,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """删除导航记录"""
    success = navigation_record_service.delete_record(record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导航记录不存在"
        )

@router.put("/{record_id}/complete", response_model=NavigationRecordResponse)
async def complete_navigation_record(
    record_id: int,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """完成导航记录"""
    completed_record = navigation_record_service.complete_record(record_id)
    if not completed_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导航记录不存在"
        )
    return completed_record

@router.put("/{record_id}/cancel", response_model=NavigationRecordResponse)
async def cancel_navigation_record(
    record_id: int,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    cancelled_record = navigation_record_service.cancel_record(record_id)
    if not cancelled_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导航记录不存在"
        )
    return cancelled_record
