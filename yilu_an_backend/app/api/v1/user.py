from fastapi import APIRouter, Depends
from app.dependencies import get_current_active_user, get_user_service
from app.schemas.user import UserResponse, UserUpdate
from app.models import User
from app.services.user import UserService

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """更新用户信息
    
    Args:
        user_update: 更新用户信息的请求体
    - nickname: 昵称（可选）
    - avatar_url: 头像URL（可选）
    - phone: 手机号（可选）
    """
    updated_user = user_service.update_user(current_user, user_update)
    return UserResponse.model_validate(updated_user)

@router.get("/bindings")
async def get_user_bindings(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户的绑定关系"""
    return user_service.get_user_bindings(current_user)
