from sqlalchemy.orm import Session
from app.models.binding import Binding, BindingStatus
from typing import List, Optional
from datetime import datetime

class BindingRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, binding_id: int) -> Optional[Binding]:
        """根据ID获取绑定关系"""
        return self.db.query(Binding).filter(Binding.id == binding_id).first()
    
    def get_by_elderly_id(self, elderly_id: int) -> List[Binding]:
        """根据老人ID获取绑定关系"""
        return self.db.query(Binding).filter(Binding.elderly_id == elderly_id).all()
    
    def get_by_family_id(self, family_id: int) -> List[Binding]:
        """根据家属ID获取绑定关系"""
        return self.db.query(Binding).filter(Binding.family_id == family_id).all()
    
    def get_by_status(self, status: BindingStatus) -> List[Binding]:
        """根据状态获取绑定关系"""
        return self.db.query(Binding).filter(Binding.status == status).all()
    
    def get_pending_bindings(self) -> List[Binding]:
        """获取待处理的绑定请求"""
        return self.db.query(Binding).filter(Binding.status == BindingStatus.PENDING).all()
    
    def get_binding_by_elderly_and_family(self, elderly_id: int, family_id: int) -> Optional[Binding]:
        """根据老人和家属ID获取绑定关系"""
        return self.db.query(Binding).filter(
            Binding.elderly_id == elderly_id,
            Binding.family_id == family_id
        ).first()
    
    def create(self, binding: Binding) -> Binding:
        """创建绑定关系"""
        self.db.add(binding)
        self.db.commit()
        self.db.refresh(binding)
        return binding
    
    def update(self, binding: Binding) -> Binding:
        """更新绑定关系"""
        if binding.status == BindingStatus.ACCEPTED and not binding.approved_at:
            binding.approved_at = datetime.now()
        self.db.commit()
        self.db.refresh(binding)
        return binding
    
    def delete(self, binding: Binding) -> None:
        """删除绑定关系"""
        self.db.delete(binding)
        self.db.commit()
    
    def exists_binding(self, elderly_id: int, family_id: int) -> bool:
        """检查绑定关系是否存在"""
        return self.db.query(Binding).filter(
            Binding.elderly_id == elderly_id,
            Binding.family_id == family_id
        ).first() is not None
