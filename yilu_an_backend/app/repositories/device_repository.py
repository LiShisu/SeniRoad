from sqlalchemy.orm import Session
from app.models.device import Device
from typing import List, Optional

class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, device_id: int) -> Optional[Device]:
        """根据ID获取设备"""
        return self.db.query(Device).filter(Device.device_id == device_id).first()
    
    def get_by_token(self, device_token: str) -> Optional[Device]:
        """根据设备token获取设备"""
        return self.db.query(Device).filter(Device.device_token == device_token).first()
    
    def get_by_user_id(self, user_id: int) -> List[Device]:
        """根据用户ID获取设备列表"""
        return self.db.query(Device).filter(Device.user_id == user_id).all()
    
    def get_active_devices(self) -> List[Device]:
        """获取所有活跃设备"""
        return self.db.query(Device).filter(Device.status == 1).all()
    
    def get_devices_by_status(self, status: int) -> List[Device]:
        """根据状态获取设备列表"""
        return self.db.query(Device).filter(Device.status == status).all()
    
    def create(self, device: Device) -> Device:
        """创建设备"""
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device
    
    def update(self, device: Device) -> Device:
        """更新设备"""
        self.db.commit()
        self.db.refresh(device)
        return device
    
    def delete(self, device: Device) -> None:
        """删除设备"""
        self.db.delete(device)
        self.db.commit()
    
    def exists_by_token(self, device_token: str) -> bool:
        """检查设备token是否已存在"""
        return self.db.query(Device).filter(Device.device_token == device_token).first() is not None
