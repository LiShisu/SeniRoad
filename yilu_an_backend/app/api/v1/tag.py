from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.services.tag import TagService
from app.dependencies import get_tag_service, get_current_active_user
from app.models import User

router = APIRouter()

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    tag_service: TagService = Depends(get_tag_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        return tag_service.create_tag(tag)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[TagResponse])
async def get_tags(
    active_only: bool = False,
    tag_service: TagService = Depends(get_tag_service),
    current_user: User = Depends(get_current_active_user)
):
    if active_only:
        return tag_service.get_active_tags()
    return tag_service.get_all_tags()

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    tag_service: TagService = Depends(get_tag_service),
    current_user: User = Depends(get_current_active_user)
):
    tag = tag_service.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    return tag

@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag: TagUpdate,
    tag_service: TagService = Depends(get_tag_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        updated_tag = tag_service.update_tag(tag_id, tag)
        if not updated_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="标签不存在"
            )
        return updated_tag
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    tag_service: TagService = Depends(get_tag_service),
    current_user: User = Depends(get_current_active_user)
):
    success = tag_service.delete_tag(tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
