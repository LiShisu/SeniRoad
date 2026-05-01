from sqlalchemy.orm import Session
from app.models.favorite_place import FavoritePlace
from typing import List, Optional

class FavoritePlaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, place_id: int) -> Optional[FavoritePlace]:
        return self.db.query(FavoritePlace).filter(FavoritePlace.place_id == place_id).first()

    def get_by_user_id(self, user_id: int) -> List[FavoritePlace]:
        return self.db.query(FavoritePlace).filter(FavoritePlace.user_id == user_id).all()

    def get_by_user_and_source(self, user_id: int, source_type: int) -> List[FavoritePlace]:
        return self.db.query(FavoritePlace).filter(
            FavoritePlace.user_id == user_id,
            FavoritePlace.source_type == source_type
        ).all()

    def get_active_places(self, user_id: int) -> List[FavoritePlace]:
        return self.db.query(FavoritePlace).filter(
            FavoritePlace.user_id == user_id,
            FavoritePlace.is_active == True
        ).all()

    def exists_by_name(self, user_id: int, place_name: str) -> bool:
        return self.db.query(FavoritePlace).filter(
            FavoritePlace.user_id == user_id,
            FavoritePlace.place_name == place_name
        ).first() is not None

    def create(self, place: FavoritePlace) -> FavoritePlace:
        self.db.add(place)
        self.db.commit()
        self.db.refresh(place)
        return place

    def update(self, place: FavoritePlace) -> FavoritePlace:
        self.db.commit()
        self.db.refresh(place)
        return place

    def delete(self, place: FavoritePlace) -> None:
        self.db.delete(place)
        self.db.commit()
