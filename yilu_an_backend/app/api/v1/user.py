from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.dependencies import get_current_active_user
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate
from app.models import User
from sqlalchemy.orm import Session

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
    db: Session = Depends(get_db)
):
    """更新用户信息
    
    - nickname: 昵称（可选）
    - avatar_url: 头像URL（可选）
    """
    user_repo = UserRepository(db)
    
    # 更新用户信息
    if user_update.nickname is not None:
        current_user.nickname = user_update.nickname
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    updated_user = user_repo.update(current_user)
    return UserResponse.model_validate(updated_user)

@router.get("/bindings")
async def get_user_bindings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的绑定关系"""
    # 这里可以根据实际的绑定关系实现
    return {
        "elderly_bindings": [binding.family for binding in current_user.bindings_elderly if binding.status == "accepted"],
        "family_bindings": [binding.elderly for binding in current_user.bindings_family if binding.status == "accepted"]
    }
