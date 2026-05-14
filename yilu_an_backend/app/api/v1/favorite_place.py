from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.schemas.favorite_place import FavoritePlaceCreate, FavoritePlaceUpdate, FavoritePlaceResponse
from app.services.favorite_place import FavoritePlaceService
from app.dependencies import get_favorite_place_service, get_current_active_user
from app.models import User, UserRole
from app.schemas.base import Result
from app.schemas.exception import BusinessException
router = APIRouter()

@router.post("/", response_model=Result[FavoritePlaceResponse], status_code=status.HTTP_201_CREATED)
async def create_favorite_place(
    place: FavoritePlaceCreate,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service)
):
    """家属为老人创建常用地点"""
    created_place = favorite_place_service.create_place(place)
    return Result(code=200, message="常用地点创建成功", data=created_place)

@router.get("/", response_model=Result[List[FavoritePlaceResponse]])
async def get_favorite_places(
    user_id: int = None,
    source_type: int = None,
    tag_id: int = None,
    active_only: bool = False,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """获取常用地点列表
    
    - user_id: 用户ID
    - source_type: 来源类型（可选，1-家属预设, 2-自动识别）
    - active_only: 是否只获取活跃地点
    """
    if user_id is None:
        if current_user.role == UserRole.ELDERLY:
           user_id = current_user.user_id
        else:
            raise BusinessException(code=400, message="家属查询时缺少老人的 user_id 参数")
    
    if active_only:
        favorite_place_service.get_active_places(user_id)
    if source_type is not None:
        favorite_place_service.get_places_by_user_and_source(user_id, source_type)
    if tag_id is not None:
        favorite_place_service.get_places_by_tag(tag_id)
    else:
        places = favorite_place_service.get_places_by_user_id(user_id)
    return Result(code=200, message="常用地点列表获取成功", data=places)

@router.get("/{place_id}", response_model=Result[FavoritePlaceResponse])
async def get_favorite_place(
    place_id: int,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取常用地点"""
    place = favorite_place_service.get_place_by_id(place_id)
    return Result(code=200, message="常用地点信息获取成功", data=place)

@router.put("/{place_id}", response_model=Result[FavoritePlaceResponse])
async def update_favorite_place(
    place_id: int,
    place: FavoritePlaceUpdate,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """更新常用地点"""
    updated_place = favorite_place_service.update_place(place_id, place)
    return Result(code=200, message="常用地点信息更新成功", data=updated_place)

@router.delete("/{place_id}", response_model=Result[None])
async def delete_favorite_place(
    place_id: int,
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    current_user: User = Depends(get_current_active_user)
):
    """删除常用地点"""
    favorite_place_service.delete_place(place_id)
    return Result(code=200, message="地点已删除")

# @router.put("/{place_id}/deactivate", response_model=FavoritePlaceResponse)
# async def deactivate_favorite_place(
#     place_id: int,
#     favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
#     current_user: User = Depends(get_current_active_user)
# ):
#     """停用常用地点"""
#     deactivated_place = favorite_place_service.deactivate_place(place_id)
#     if not deactivated_place:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="常用地点不存在"
#         )
#     return deactivated_place
