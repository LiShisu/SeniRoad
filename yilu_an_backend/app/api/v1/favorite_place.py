from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.favorite_place import FavoritePlaceCreate, FavoritePlaceUpdate, FavoritePlaceResponse
from app.services.favorite_place import FavoritePlaceService
from app.dependencies import get_favorite_place_service, get_current_active_user
from app.models import User

router = APIRouter()

@router.post("/", response_model=FavoritePlaceResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite_place(
    place: FavoritePlaceCreate,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """创建常用地点"""
    try:
        return favorite_place_service.create_place(place)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[FavoritePlaceResponse])
async def get_favorite_places(
    user_id: int,
    source_type: int = None,
    active_only: bool = False,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取常用地点列表
    
    - user_id: 用户ID
    - source_type: 来源类型（可选，1-家属预设, 2-自动识别）
    - active_only: 是否只获取活跃地点
    """
    if active_only:
        return favorite_place_service.get_active_places(user_id)
    if source_type:
        return favorite_place_service.get_places_by_user_and_source(user_id, source_type)
    return favorite_place_service.get_places_by_user_id(user_id)

@router.get("/{place_id}", response_model=FavoritePlaceResponse)
async def get_favorite_place(
    place_id: int,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取常用地点"""
    place = favorite_place_service.get_place_by_id(place_id)
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="常用地点不存在"
        )
    return place

@router.put("/{place_id}", response_model=FavoritePlaceResponse)
async def update_favorite_place(
    place_id: int,
    place: FavoritePlaceUpdate,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """更新常用地点"""
    try:
        updated_place = favorite_place_service.update_place(place_id, place)
        if not updated_place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="常用地点不存在"
            )
        return updated_place
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite_place(
    place_id: int,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """删除常用地点"""
    success = favorite_place_service.delete_place(place_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="常用地点不存在"
        )

@router.patch("/{place_id}/deactivate", response_model=FavoritePlaceResponse)
async def deactivate_favorite_place(
    place_id: int,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """停用常用地点"""
    deactivated_place = favorite_place_service.deactivate_place(place_id)
    if not deactivated_place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="常用地点不存在"
        )
    return deactivated_place
