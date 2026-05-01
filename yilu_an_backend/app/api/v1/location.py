from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.dependencies import get_current_active_user, get_location_service
from app.services.location import LocationService
from app.schemas.location import LocationCreate, LocationResponse
from app.models import User
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.post("/update", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def update_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    return location_service.create_location(
        user_id=current_user.user_id,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        address=location_data.address,
        accuracy=location_data.accuracy,
        record_id=location_data.record_id
    )

@router.get("/history", response_model=List[LocationResponse])
async def get_location_history(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    return location_service.get_by_user_id(
        user_id=current_user.user_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )

@router.get("/latest", response_model=LocationResponse)
async def get_latest_location(
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    location = location_service.get_latest_by_user_id(current_user.user_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="位置记录不存在"
        )
    return location

@router.get("/record/{record_id}", response_model=List[LocationResponse])
async def get_location_by_record(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    return location_service.get_by_record_id(record_id)

@router.get("/{location_id}", response_model=LocationResponse)
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
    return location

@router.delete("/user/{user_id}/old", response_model=dict)
async def delete_old_locations(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    location_service: LocationService = Depends(get_location_service)
):
    deleted_count = location_service.delete_old_locations(user_id, days)
    return {"deleted_count": deleted_count}
