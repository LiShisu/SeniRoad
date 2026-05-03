from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies.services import get_binding_service
from app.dependencies.auth import get_current_active_user
from app.services.binding import BindingService
from app.schemas.binding import BindingCreate, BindingResponse, BindingUnbind
from app.models import User

router = APIRouter()

@router.post("/bind", response_model=BindingResponse, status_code=status.HTTP_201_CREATED)
async def create_binding(
    binding_data: BindingCreate,
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        binding_data.family_id = current_user.user_id
        return binding_service.create_binding(binding_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=list[BindingResponse])
async def list_bindings(
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
    return binding_service.get_bindings_for_user(
        user_id=current_user.user_id,
        user_role=current_user.role
    )

@router.post("/unbind", status_code=status.HTTP_204_NO_CONTENT)
async def unbind(
    unbind_data: BindingUnbind,
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        unbind_data.family_id = current_user.user_id
        binding_service.unbind(unbind_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# TODO: 审核机制
@router.put("/{binding_id}/approve", response_model=BindingResponse)
async def approve_binding(
    binding_id: int,
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        return binding_service.approve_binding(binding_id, current_user.user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.put("/{binding_id}/reject", response_model=BindingResponse)
async def reject_binding(
    binding_id: int,
    binding_service: BindingService = Depends(get_binding_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        return binding_service.reject_binding(binding_id, current_user.user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
