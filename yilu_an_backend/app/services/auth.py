from app.utils import hash_password, verify_password
from app.utils.security import create_access_token
from app.repositories.user_repository import UserRepository
from app.models import User
from app.schemas.user import UserCreate, LoginResponse, WechatUserCreate
from fastapi import HTTPException, status

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def hash_password(self, password: str) -> str:
        return hash_password(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)
    
    async def register(self, user_data: UserCreate):
        """用户注册"""
        # 检查手机号是否已存在
        if self.user_repository.exists_by_phone(user_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # 创建新用户
        hashed_password = self.hash_password(user_data.password)
        db_user = User(
            phone=user_data.phone,
            nickname=user_data.nickname,
            password=hashed_password,
            role=user_data.role,
            avatar_url=user_data.avatar_url,
            is_active=True
        )
        
        # 保存用户
        return self.user_repository.create(db_user)
    
    async def login(self, phone: str, password: str) -> LoginResponse:
        """用户登录"""
        # 查找用户
        user = self.user_repository.get_by_phone(phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证密码
        if not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成访问令牌
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        
        return LoginResponse(access_token=access_token)
    
    async def wechat_register(self, wechat_data: WechatUserCreate):
        """微信小程序用户注册"""
        # 检查openid是否已存在
        if self.user_repository.exists_by_openid(wechat_data.openid):
            # 如果openid已存在，返回现有用户
            return self.user_repository.get_by_openid(wechat_data.openid)
        
        # 检查unionid是否已存在
        if wechat_data.unionid and self.user_repository.exists_by_unionid(wechat_data.unionid):
            # 如果unionid已存在，返回现有用户
            return self.user_repository.get_by_unionid(wechat_data.unionid)
        
        # 创建新用户
        db_user = User(
            openid=wechat_data.openid,
            unionid=wechat_data.unionid,
            session_key=wechat_data.session_key,
            nickname=wechat_data.nickname,
            avatar_url=wechat_data.avatar_url,
            role=wechat_data.role,
            is_active=True
        )
        
        # 保存用户
        return self.user_repository.create(db_user)
    
    async def wechat_login(self, openid: str, session_key: str) -> LoginResponse:
        """微信小程序用户登录"""
        # 查找用户
        user = self.user_repository.get_by_openid(openid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 更新session_key
        user.session_key = session_key
        self.user_repository.update(user)
        
        # 生成访问令牌
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        
        return LoginResponse(access_token=access_token)

