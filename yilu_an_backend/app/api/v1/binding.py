from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies.services import get_binding_service
from app.dependencies.auth import get_current_active_user
from app.services.binding import BindingService
from app.schemas.binding import BindingCreate, BindingResponse, BindingUnbind,BindingStatusUpdate
from app.models import User
from app.schemas.base import Result
router = APIRouter()

@router.post("/", response_model=Result[BindingResponse], status_code=status.HTTP_201_CREATED)
async def create_binding(
    binding_data: BindingCreate,
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
# 业务服务直接读取当前登录用户作为发起方（家属）
    binding = binding_service.create_binding(binding_data.elderly_phone, current_user.user_id)
    return Result(code=200, message="亲属绑定请求已发送", data=binding)

@router.get("/", response_model=Result[list[BindingResponse]])
async def list_bindings(
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
    bindings = binding_service.get_bindings_for_user(current_user.user_id, current_user.role)
    return Result(code=200, message="亲属绑定列表获取成功", data=bindings)

@router.delete("/{binding_id}", response_model=Result[None])
async def unbind(
    binding_id: int,
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
    """解除绑定 (资源删除)"""
    binding_service.delete_binding(binding_id, current_user.user_id)
    return Result(code=200, message="已解除绑定")
# TODO: 审核机制
# @router.put("/{binding_id}/approve", response_model=BindingResponse)
# async def approve_binding(
#     binding_id: int,
#     binding_service: BindingService = Depends(get_binding_service),
#     current_user: User = Depends(get_current_active_user)
# ):
#     try:
#         return binding_service.approve_binding(binding_id, current_user.user_id)
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(e)
#         )
#     except PermissionError as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=str(e)
#         )

# @router.put("/{binding_id}/reject", response_model=BindingResponse)
# async def reject_binding(
#     binding_id: int,
#     binding_service: BindingService = Depends(get_binding_service),
#     current_user: User = Depends(get_current_active_user)
# ):
#     try:
#         return binding_service.reject_binding(binding_id, current_user.user_id)
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(e)
#         )
#     except PermissionError as e:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=str(e)
#         )
@router.put("/{binding_id}", response_model=Result[BindingResponse])
async def update_binding_status(
    binding_id: int,
    update_data: BindingStatusUpdate,
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
    """处理绑定请求：同意/拒绝"""
    binding = binding_service.update_binding_status(binding_id, update_data.status, current_user.user_id)
    return Result(code=200, msg="绑定状态已更新", data=binding)