from app.repositories.user_repository import UserRepository
from app.models import User
from app.models.user import UserRole
from app.schemas.user import UserUpdate

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def get_user_by_id(self, user_id: int) -> User:
        """根据ID获取用户信息"""
        return self.user_repository.get_by_id(user_id)
    
    def update_user(self, user: User, user_update: UserUpdate) -> User:
        """更新用户信息"""
        # 更新用户信息
        if user_update.nickname is not None:
            user.nickname = user_update.nickname
        if user_update.gender is not None:
            user.gender = user_update.gender
        if user_update.birthday is not None:
            user.birthday = user_update.birthday
        if user_update.avatar_url is not None:
            user.avatar_url = user_update.avatar_url
        if user_update.phone is not None:
            user.phone = user_update.phone
        
        # 保存更新
        return self.user_repository.update(user)
    
    def get_user_bindings(self, user: User):
        """获取用户的绑定关系"""
        if user.role == UserRole.FAMILY:
            # 获取已接受的老人绑定
            elderly_bindings = [binding.family for binding in user.bindings_elderly if binding.status == "accepted"]
            return {
                "elderly_bindings": elderly_bindings
            }
        else:
            # 获取已接受的家属绑定
            family_bindings = [binding.elderly for binding in user.bindings_family if binding.status == "accepted"]
            return {
                "family_bindings": family_bindings
            }
