from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.services.device import DeviceService
from app.dependencies import get_device_service, get_current_active_user
from app.models import User

router = APIRouter()

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device: DeviceCreate,
    device_service: DeviceService = Depends(get_device_service),
    current_user: User = Depends(get_current_active_user)
):
    """创建设备"""
    try:
        return device_service.create_device(device)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[DeviceResponse])
async def get_devices(
    user_id: int = None,
    device_service: DeviceService = Depends(get_device_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备列表
    
    - 如果提供了user_id，获取指定用户的设备
    - 否则获取所有活跃设备
    """
    if user_id:
        return device_service.get_devices_by_user_id(user_id)
    return device_service.get_active_devices()

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    device_service: DeviceService = Depends(get_device_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取设备"""
    device = device_service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    return device

@router.get("/token/{device_token}", response_model=DeviceResponse)
async def get_device_by_token(
    device_token: str,
    device_service: DeviceService = Depends(get_device_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据设备token获取设备"""
    device = device_service.get_device_by_token(device_token)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device: DeviceUpdate,
    device_service: DeviceService = Depends(get_device_service),
    current_user: User = Depends(get_current_active_user)
):
    """更新设备"""
    updated_device = device_service.update_device(device_id, device)
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    return updated_device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    device_service: DeviceService = Depends(get_device_service),
    current_user: User = Depends(get_current_active_user)
):
    """删除设备"""
    success = device_service.delete_device(device_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

@router.patch("/{device_id}/status/{status}", response_model=DeviceResponse)
async def update_device_status(
    device_id: int,
    status: int,
    device_service: DeviceService = Depends(get_device_service),
    current_user: User = Depends(get_current_active_user)
):
    """更新设备状态"""
    if status not in [0, 1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="状态值必须为0（离线）或1（在线）"
        )
    updated_device = device_service.update_device_status(device_id, status)
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    return updated_device
