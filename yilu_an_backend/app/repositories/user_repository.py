from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from typing import List, Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return self.db.query(User).filter(User.phone == phone).first()
    
    def get_by_role(self, role: UserRole) -> List[User]:
        """根据角色获取用户列表"""
        return self.db.query(User).filter(User.role == role).all()
    
    def get_active_users(self) -> List[User]:
        """获取所有活跃用户"""
        return self.db.query(User).filter(User.is_active == True).all()
    
    def create(self, user: User) -> User:
        """创建用户"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        """更新用户"""
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """删除用户"""
        self.db.delete(user)
        self.db.commit()
    
    def exists_by_phone(self, phone: str) -> bool:
        """检查手机号是否已存在"""
        return self.db.query(User).filter(User.phone == phone).first() is not None
    
    def get_by_openid(self, openid: str) -> Optional[User]:
        """根据openid获取用户"""
        return self.db.query(User).filter(User.openid == openid).first()
    
    def get_by_openid_and_role(self, openid: str, role: UserRole) -> Optional[User]:
        """根据openid和role获取用户"""
        return self.db.query(User).filter(User.openid == openid, User.role == role).first()
    
    def exists_by_openid(self, openid: str) -> bool:
        """检查openid是否已存在"""
        return self.db.query(User).filter(User.openid == openid).first() is not None