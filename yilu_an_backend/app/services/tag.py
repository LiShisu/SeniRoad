from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.repositories.tag_repository import TagRepository
from typing import List, Optional

class TagService:
    def __init__(self, tag_repo: TagRepository):
        self.tag_repo = tag_repo

    def get_tag_by_id(self, tag_id: int) -> Optional[TagResponse]:
        tag = self.tag_repo.get_by_id(tag_id)
        if tag:
            return TagResponse.model_validate(tag)
        return None

    def get_all_tags(self) -> List[TagResponse]:
        tags = self.tag_repo.get_all()
        return [TagResponse.model_validate(tag) for tag in tags]

    def get_active_tags(self) -> List[TagResponse]:
        tags = self.tag_repo.get_active_tags()
        return [TagResponse.model_validate(tag) for tag in tags]

    def create_tag(self, tag_data: TagCreate) -> TagResponse:
        if self.tag_repo.exists_by_name(tag_data.tag_name):
            raise ValueError("标签名称已存在")

        tag = Tag(
            tag_name=tag_data.tag_name,
            color=tag_data.color,
            icon=tag_data.icon,
            is_active=tag_data.is_active
        )

        created_tag = self.tag_repo.create(tag)
        return TagResponse.model_validate(created_tag)

    def update_tag(self, tag_id: int, tag_data: TagUpdate) -> Optional[TagResponse]:
        tag = self.tag_repo.get_by_id(tag_id)
        if not tag:
            return None

        if tag_data.tag_name is not None:
            if tag_data.tag_name != tag.tag_name and \
               self.tag_repo.exists_by_name(tag_data.tag_name):
                raise ValueError("标签名称已存在")
            tag.tag_name = tag_data.tag_name
        if tag_data.color is not None:
            tag.color = tag_data.color
        if tag_data.icon is not None:
            tag.icon = tag_data.icon
        if tag_data.is_active is not None:
            tag.is_active = tag_data.is_active

        updated_tag = self.tag_repo.update(tag)
        return TagResponse.model_validate(updated_tag)

    def delete_tag(self, tag_id: int) -> bool:
        tag = self.tag_repo.get_by_id(tag_id)
        if not tag:
            return False
        self.tag_repo.delete(tag)
        return True
