from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from app.schemas.navigation_record import NavigationRecordCreate, NavigationRecordUpdate, NavigationRecordResponse
from app.services.navigation_record import NavigationRecordService
from app.dependencies import get_navigation_record_service, get_current_active_user
from app.models import User
from app.schemas.base import Result
from app.schemas.exception import BusinessException,NotFoundException,ForbiddenException,UnauthorizedException
router = APIRouter()

@router.post("/", response_model=Result[NavigationRecordResponse])
async def create_navigation_record(
    record: NavigationRecordCreate,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    record.user_id = current_user.user_id
    created_record = navigation_record_service.create_record(record)
    return Result(
        code=200, # 或者 201
        message="导航记录创建成功",
        data=created_record
    )

@router.get("/", response_model=Result[List[NavigationRecordResponse]])
async def get_navigation_records(
    user_id: int = Query(..., description="老人ID", gt=0),
    status_filter: Optional[int] = Query(None, alias="status", ge=1, le=3, description="状态: 1-进行中, 2-完成, 3-取消"),
    start_date: Optional[datetime] = Query(None, description="起始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
):
    """
    获取当前用户的导航记录列表 
    """
    # if status_filter is not None:
    #     records = navigation_record_service.get_records_by_status(user_id, status_filter)
    # else:
    records = navigation_record_service.get_records_by_user_id(user_id)
    return Result(code=200, message="导航记录列表查询成功", data=records)

@router.get("/{record_id}", response_model=Result[NavigationRecordResponse])
async def get_navigation_record(
    record_id: int,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取导航记录"""
    record = navigation_record_service.get_record_by_id(record_id)
    if not record:
        raise BusinessException(code=400, message="导航记录不存在")
    return Result(code=200, message="success", data=record)

@router.put("/{record_id}", response_model=Result[NavigationRecordResponse])
async def update_navigation_record(
    record_id: int,
    update_data: NavigationRecordUpdate,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """更新导航记录"""
    record = navigation_record_service.get_record_by_id(record_id)
    if not record:
        raise BusinessException(code=400, message="导航记录不存在")
    updated_record = navigation_record_service.update_record(record_id, update_data)
    return Result(code=200, message="导航记录更新成功", data=updated_record)

@router.delete("/{record_id}", response_model=Result)
async def delete_navigation_record(
    record_id: int,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """删除导航记录"""
    record = navigation_record_service.get_record_by_id(record_id)
    if not record:
        raise BusinessException(code=400, message="导航记录不存在")
    success = navigation_record_service.delete_record(record_id)
    if not success:
        raise BusinessException(code=400, message="删除失败，请稍后重试")
        
    return Result(code=200, message="导航记录删除成功", data=None)

@router.put("/{record_id}/complete", response_model=Result[NavigationRecordResponse])
async def complete_navigation_record(
    record_id: int,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """完成导航"""
    record = navigation_record_service.get_record_by_id(record_id)
    if not record:
        raise BusinessException(code=400, message="导航记录不存在")
    if record.status == 2:
         raise BusinessException(code=400, message="该导航记录已处于完成状态")

    completed_record = navigation_record_service.complete_record(record_id)
    return Result(code=200, message="导航已标记为完成", data=completed_record)

@router.put("/{record_id}/cancel", response_model=Result[NavigationRecordResponse])
async def cancel_navigation_record(
    record_id: int,
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    current_user: User = Depends(get_current_active_user)
):
    """取消导航"""
    record = navigation_record_service.get_record_by_id(record_id)
    if not record:
        raise BusinessException(code=400, message="导航记录不存在")
    if record.status == 3:
         raise BusinessException(code=400, detail="该导航记录已处于取消状态")
    cancelled_record = navigation_record_service.cancel_record(record_id)
    return Result(code=200, message="导航已取消", data=cancelled_record)
