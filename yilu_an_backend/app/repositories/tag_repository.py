from sqlalchemy.orm import Session
from app.models.tag import Tag
from typing import List, Optional

class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        return self.db.query(Tag).filter(Tag.tag_id == tag_id).first()

    def get_all(self) -> List[Tag]:
        return self.db.query(Tag).all()

    def get_active_tags(self) -> List[Tag]:
        return self.db.query(Tag).filter(Tag.is_active == True).all()

    def exists_by_name(self, tag_name: str) -> bool:
        return self.db.query(Tag).filter(Tag.tag_name == tag_name).first() is not None

    def create(self, tag: Tag) -> Tag:
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def update(self, tag: Tag) -> Tag:
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete(self, tag: Tag) -> None:
        self.db.delete(tag)
        self.db.commit()
