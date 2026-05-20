from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.dependencies import get_current_active_user, get_location_service
from app.services.location import LocationService
from app.schemas.location import LocationCreate, LocationResponse
from app.models import User
from typing import List, Optional
from datetime import datetime
from app.schemas.base import Result

router = APIRouter()

@router.post("/", response_model=Result[LocationResponse], status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    location = location_service.create_location(
        user_id=current_user.user_id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        address=location_data.address,
        accuracy=location_data.accuracy,
        record_id=location_data.record_id
    )
    return Result(code=200, message="位置记录创建成功", data=location)

@router.get("/history", response_model=Result[List[LocationResponse]])
async def get_location_history(
    user_id: int = None,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    locations = location_service.get_by_user_id(
        user_id=user_id or current_user.user_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
    return Result(code=200, message="位置历史查询成功", data=locations)

@router.get("/latest", response_model=Result[LocationResponse])
async def get_latest_location(
    user_id: int = None,
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    location = location_service.get_latest_by_user_id(user_id or current_user.user_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="位置记录不存在"
        )
    return Result(code=200, message="success", data=location)

@router.get("/record/{record_id}", response_model=Result[List[LocationResponse]])
async def get_location_by_record(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    locations = location_service.get_by_record_id(record_id)
    return Result(code=200, message="位置记录查询成功", data=locations)

@router.get("/{location_id}", response_model=Result[LocationResponse])
async def get_location(
    location_id: int,
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    location = location_service.get_by_id(location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="位置记录不存在"
        )
    return Result(code=200, message="位置记录查询成功", data=location)

@router.delete("/user/{user_id}/old", response_model=Result[dict])
async def delete_old_locations(
    user_id: int = None,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    user_id = user_id or current_user.user_id
    deleted_count = location_service.delete_old_locations(user_id, days)
    return Result(code=200, message="删除成功", data={"deleted_count": deleted_count})
