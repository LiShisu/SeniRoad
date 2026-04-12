from sqlalchemy.orm import Session
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.repositories.device_repository import DeviceRepository
from typing import List, Optional
from datetime import datetime

class DeviceService:
    def __init__(self, db: Session):
        self.device_repo = DeviceRepository(db)
    
    def get_device_by_id(self, device_id: int) -> Optional[DeviceResponse]:
        """根据ID获取设备"""
        device = self.device_repo.get_by_id(device_id)
        if device:
            return DeviceResponse.model_validate(device)
        return None
    
    def get_device_by_token(self, device_token: str) -> Optional[DeviceResponse]:
        """根据设备token获取设备"""
        device = self.device_repo.get_by_token(device_token)
        if device:
            return DeviceResponse.model_validate(device)
        return None
    
    def get_devices_by_user_id(self, user_id: int) -> List[DeviceResponse]:
        """根据用户ID获取设备列表"""
        devices = self.device_repo.get_by_user_id(user_id)
        return [DeviceResponse.model_validate(device) for device in devices]
    
    def get_active_devices(self) -> List[DeviceResponse]:
        """获取所有活跃设备"""
        devices = self.device_repo.get_active_devices()
        return [DeviceResponse.model_validate(device) for device in devices]
    
    def create_device(self, device_data: DeviceCreate) -> DeviceResponse:
        """创建设备"""
        # 检查设备token是否已存在
        if self.device_repo.exists_by_token(device_data.device_token):
            raise ValueError("设备token已存在")
        
        # 创建设备实例
        device = Device(
            user_id=device_data.user_id,
            device_token=device_data.device_token,
            device_model=device_data.device_model,
            status=device_data.status,
            last_login_time=datetime.now()
        )
        
        # 保存设备
        created_device = self.device_repo.create(device)
        return DeviceResponse.model_validate(created_device)
    
    def update_device(self, device_id: int, device_data: DeviceUpdate) -> Optional[DeviceResponse]:
        """更新设备"""
        device = self.device_repo.get_by_id(device_id)
        if not device:
            return None
        
        # 更新设备字段
        if device_data.device_model is not None:
            device.device_model = device_data.device_model
        if device_data.last_login_time is not None:
            device.last_login_time = device_data.last_login_time
        if device_data.status is not None:
            device.status = device_data.status
        
        # 保存更新
        updated_device = self.device_repo.update(device)
        return DeviceResponse.model_validate(updated_device)
    
    def delete_device(self, device_id: int) -> bool:
        """删除设备"""
        device = self.device_repo.get_by_id(device_id)
        if not device:
            return False
        
        self.device_repo.delete(device)
        return True
    
    def update_device_status(self, device_id: int, status: int) -> Optional[DeviceResponse]:
        """更新设备状态"""
        device = self.device_repo.get_by_id(device_id)
        if not device:
            return None
        
        device.status = status
        if status == 1:  # 在线状态
            device.last_login_time = datetime.now()
        
        updated_device = self.device_repo.update(device)
        return DeviceResponse.model_validate(updated_device)
