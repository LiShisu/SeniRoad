from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.dependencies import get_current_active_user
from app.repositories.location_repository import LocationRepository
from app.schemas.location import LocationCreate, LocationResponse
from app.models import User
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/update", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def update_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新实时位置
    
    - latitude: 纬度（-90到90之间）
    - longitude: 经度（-180到180之间）
    - address: 地址（可选）
    - accuracy: 精度（可选）
    """
    location_repo = LocationRepository(db)
    location = location_repo.create_location(
        user_id=current_user.id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        address=location_data.address,
        accuracy=location_data.accuracy
    )
    return LocationResponse.model_validate(location)

@router.get("/history", response_model=List[LocationResponse])
async def get_location_history(
    start_time: datetime = None,
    end_time: datetime = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """查询历史轨迹
    
    - start_time: 开始时间（可选）
    - end_time: 结束时间（可选）
    - limit: 返回记录数量限制（默认100）
    """
    location_repo = LocationRepository(db)
    locations = location_repo.get_by_user_id(
        user_id=current_user.id,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
    return [LocationResponse.model_validate(location) for location in locations]

@router.get("/latest", response_model=LocationResponse)
async def get_latest_location(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取最新位置"""
    location_repo = LocationRepository(db)
    location = location_repo.get_latest_by_user_id(current_user.id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="位置记录不存在"
        )
    return LocationResponse.model_validate(location)
