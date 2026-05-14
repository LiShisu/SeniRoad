from fastapi import APIRouter, Depends
from app.dependencies import get_current_active_user, get_user_service
from app.schemas.user import UserResponse, UserUpdate
from app.models import User
from app.services.user import UserService
from app.schemas.base import Result
from typing import Any
router = APIRouter()

@router.get("/profile", response_model=Result[UserResponse])
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前登录用户信息"""
    user_data = UserResponse.model_validate(current_user)
    return Result(code=200, message="获取成功", data=user_data)

@router.put("/profile", response_model=Result[UserResponse])
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """更新当前用户信息 (部分更新)"""
    updated_user = user_service.update_user(current_user, user_update)
    user_data = UserResponse.model_validate(updated_user)
    return Result(code=200, message="更新成功", data=user_data)

@router.get("/bindings",response_model=Result[Any])
async def get_user_bindings(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取当前用户的亲属/老人绑定关系"""
    bindings_data = user_service.get_user_bindings(current_user)
    return Result(code=200, message="获取成功", data=bindings_data)
