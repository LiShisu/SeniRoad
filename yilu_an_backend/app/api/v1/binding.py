from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.dependencies import get_current_active_user
from app.repositories.binding_repository import BindingRepository
from app.schemas.binding import BindingCreate, BindingResponse, BindingUnbind
from app.models import User
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.post("/", response_model=BindingResponse, status_code=status.HTTP_201_CREATED)
async def create_binding(
    binding_data: BindingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建绑定关系
    
    - elderly_id: 老人用户ID
    - family_id: 家属用户ID
    """
    binding_repo = BindingRepository(db)
    
    # 检查绑定关系是否已存在
    existing_binding = binding_repo.get_by_elderly_and_family(
        binding_data.elderly_id,
        binding_data.family_id
    )
    
    if existing_binding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="绑定关系已存在"
        )
    
    # 创建绑定关系
    binding = binding_repo.create(
        elderly_id=binding_data.elderly_id,
        family_id=binding_data.family_id
    )
    
    return BindingResponse.model_validate(binding)

@router.get("/", response_model=List[BindingResponse])
async def list_bindings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取绑定关系列表"""
    binding_repo = BindingRepository(db)
    
    # 根据用户角色获取绑定关系
    if current_user.role == "elderly":
        bindings = binding_repo.get_by_elderly_id(current_user.user_id)
    else:  # family
        bindings = binding_repo.get_by_family_id(current_user.user_id)
    
    return [BindingResponse.model_validate(binding) for binding in bindings]

@router.post("/unbind", status_code=status.HTTP_204_NO_CONTENT)
async def unbind(
    unbind_data: BindingUnbind,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """解除绑定关系
    
    - elderly_id: 老人用户ID
    - family_id: 家属用户ID
    """
    binding_repo = BindingRepository(db)
    
    # 检查绑定关系是否存在
    binding = binding_repo.get_by_elderly_and_family(
        unbind_data.elderly_id,
        unbind_data.family_id
    )
    
    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="绑定关系不存在"
        )
    
    # 检查用户是否有权限解除绑定
    if current_user.user_id not in [binding.elderly_id, binding.family_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权解除此绑定关系"
        )
    
    # 删除绑定关系
    binding_repo.delete(binding)

@router.put("/{binding_id}/approve", response_model=BindingResponse)
async def approve_binding(
    binding_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批准绑定请求"""
    binding_repo = BindingRepository(db)
    binding = binding_repo.get_by_id(binding_id)
    
    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="绑定关系不存在"
        )
    
    # 只有老人可以批准绑定请求
    if binding.elderly_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有老人可以批准绑定请求"
        )
    
    # 更新绑定状态
    binding.status = "accepted"
    updated_binding = binding_repo.update(binding)
    
    return BindingResponse.model_validate(updated_binding)

@router.put("/{binding_id}/reject", response_model=BindingResponse)
async def reject_binding(
    binding_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """拒绝绑定请求"""
    binding_repo = BindingRepository(db)
    binding = binding_repo.get_by_id(binding_id)
    
    if not binding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="绑定关系不存在"
        )
    
    # 只有老人可以拒绝绑定请求
    if binding.elderly_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有老人可以拒绝绑定请求"
        )
    
    # 更新绑定状态
    binding.status = "rejected"
    updated_binding = binding_repo.update(binding)
    
    return BindingResponse.model_validate(updated_binding)
