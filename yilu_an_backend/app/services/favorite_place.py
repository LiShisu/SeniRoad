from app.models.favorite_place import FavoritePlace
from app.schemas.favorite_place import FavoritePlaceCreate, FavoritePlaceUpdate, FavoritePlaceResponse
from app.repositories.favorite_place_repository import FavoritePlaceRepository
from typing import List, Optional

class FavoritePlaceService:
    def __init__(self, favorite_place_repo: FavoritePlaceRepository):
        self.favorite_place_repo = favorite_place_repo

    def get_place_by_id(self, place_id: int) -> Optional[FavoritePlaceResponse]:
        place = self.favorite_place_repo.get_by_id(place_id)
        if place:
            return FavoritePlaceResponse.model_validate(place)
        return None

    def get_places_by_user_id(self, user_id: int) -> List[FavoritePlaceResponse]:
        places = self.favorite_place_repo.get_by_user_id(user_id)
        return [FavoritePlaceResponse.model_validate(place) for place in places]

    def get_places_by_user_and_source(self, user_id: int, source_type: int) -> List[FavoritePlaceResponse]:
        places = self.favorite_place_repo.get_by_user_and_source(user_id, source_type)
        return [FavoritePlaceResponse.model_validate(place) for place in places]

    def get_places_by_tag(self, tag_id: int) -> List[FavoritePlaceResponse]:
        places = self.favorite_place_repo.get_by_tag_id(tag_id)
        return [FavoritePlaceResponse.model_validate(place) for place in places]

    def get_active_places(self, user_id: int) -> List[FavoritePlaceResponse]:
        places = self.favorite_place_repo.get_active_places(user_id)
        return [FavoritePlaceResponse.model_validate(place) for place in places]

    def create_place(self, place_data: FavoritePlaceCreate) -> FavoritePlaceResponse:
        if self.favorite_place_repo.exists_by_name(place_data.user_id, place_data.place_name):
            raise ValueError("常用地点名称已存在")

        place = FavoritePlace(
            user_id=place_data.user_id,
            place_name=place_data.place_name,
            latitude=place_data.latitude,
            longitude=place_data.longitude,
            address=place_data.address,
            source_type=place_data.source_type,
            tag_id=place_data.tag_id,
            is_active=place_data.is_active
        )

        created_place = self.favorite_place_repo.create(place)
        return FavoritePlaceResponse.model_validate(created_place)

    def update_place(self, place_id: int, place_data: FavoritePlaceUpdate) -> Optional[FavoritePlaceResponse]:
        place = self.favorite_place_repo.get_by_id(place_id)
        if not place:
            return None

        if place_data.place_name is not None:
            if place_data.place_name != place.place_name and \
               self.favorite_place_repo.exists_by_name(place.user_id, place_data.place_name):
                raise ValueError("常用地点名称已存在")
            place.place_name = place_data.place_name
        if place_data.latitude is not None:
            place.latitude = place_data.latitude
        if place_data.longitude is not None:
            place.longitude = place_data.longitude
        if place_data.address is not None:
            place.address = place_data.address
        if place_data.source_type is not None:
            place.source_type = place_data.source_type
        if place_data.tag_id is not None:
            place.tag_id = place_data.tag_id
        if place_data.is_active is not None:
            place.is_active = place_data.is_active

        updated_place = self.favorite_place_repo.update(place)
        return FavoritePlaceResponse.model_validate(updated_place)

    def delete_place(self, place_id: int) -> bool:
        place = self.favorite_place_repo.get_by_id(place_id)
        if not place:
            return False

        self.favorite_place_repo.delete(place)
        return True

    def deactivate_place(self, place_id: int) -> Optional[FavoritePlaceResponse]:
        place = self.favorite_place_repo.get_by_id(place_id)
        if not place:
            return None

        place.is_active = False
        updated_place = self.favorite_place_repo.update(place)
        return FavoritePlaceResponse.model_validate(updated_place)
