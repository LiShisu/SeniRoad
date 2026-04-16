from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.config import settings
from app.database import get_db
from app.repositories import UserRepository
from app.models import User
from app.services.auth import AuthService
from app.services.user import UserService

# OAuth2 密码流配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.OAUTH2_TOKEN_URL)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户
    
    验证 JWT 令牌并返回完整的用户信息
    
    Args:
        token: JWT 令牌
        db: 数据库会话
    
    Returns:
        User: 用户对象
    
    Raises:
        HTTPException: 认证失败时抛出
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码 JWT 令牌
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 使用 UserRepository 获取完整的用户信息
    user_repository = UserRepository(db)
    user = user_repository.get_by_id(int(user_id))
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户
    
    验证用户是否活跃
    
    Args:
        current_user: 当前用户
    
    Returns:
        User: 活跃用户对象
    
    Raises:
        HTTPException: 用户不活跃时抛出
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_user_repository(db: Session = Depends(get_db)):
    """获取用户仓库
    
    创建并返回用户仓库实例
    
    Args:
        db: 数据库会话
    
    Returns:
        UserRepository: 用户仓库实例
    """
    return UserRepository(db)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)):
    """获取认证服务
    
    创建并返回认证服务实例
    
    Args:
        user_repo: 用户仓库实例
    
    Returns:
        AuthService: 认证服务实例
    """
    return AuthService(user_repo)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)):
    """获取用户服务
    
    创建并返回用户服务实例
    
    Args:
        user_repo: 用户仓库实例
    
    Returns:
        UserService: 用户服务实例
    """
    return UserService(user_repo)
