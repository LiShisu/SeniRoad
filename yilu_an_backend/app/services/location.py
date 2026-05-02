from app.models.location import Location
from app.schemas.location import LocationCreate, LocationResponse
from app.repositories.location_repository import LocationRepository
from typing import List, Optional
from datetime import datetime, timedelta

class LocationService:
    def __init__(self, location_repo: LocationRepository):
        self.location_repo = location_repo

    def get_by_id(self, location_id: int) -> Optional[LocationResponse]:
        location = self.location_repo.get_by_id(location_id)
        if location:
            return LocationResponse.model_validate(location)
        return None

    def get_latest_by_user_id(self, user_id: int) -> Optional[LocationResponse]:
        location = self.location_repo.get_latest_by_user_id(user_id)
        if location:
            return LocationResponse.model_validate(location)
        return None

    def get_by_user_id(
        self,
        user_id: int,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 100
    ) -> List[LocationResponse]:
        locations = self.location_repo.get_by_user_id(user_id, start_time, end_time, limit)
        return [LocationResponse.model_validate(loc) for loc in locations]

    def get_by_record_id(self, record_id: int) -> List[LocationResponse]:
        locations = self.location_repo.get_by_record_id(record_id)
        return [LocationResponse.model_validate(loc) for loc in locations]

    def create_location(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        address: Optional[str] = None,
        accuracy: Optional[float] = None,
        record_id: Optional[int] = None
    ) -> LocationResponse:
        location = self.location_repo.create_location(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            address=address,
            accuracy=accuracy,
            record_id=record_id
        )
        return LocationResponse.model_validate(location)

    def create(self, location_data: LocationCreate) -> LocationResponse:
        location = Location(
            user_id=location_data.user_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            address=location_data.address,
            accuracy=location_data.accuracy,
            record_id=location_data.record_id
        )
        created = self.location_repo.create(location)
        return LocationResponse.model_validate(created)

    def bulk_create(self, locations: List[Location]) -> List[Location]:
        return self.location_repo.bulk_create(locations)

    def get_track_by_record_id(self, record_id: int) -> List[LocationResponse]:
        return self.get_by_record_id(record_id)

    def delete_old_locations(self, user_id: int, days: int = 30) -> int:
        before_time = datetime.now() - timedelta(days=days)
        return self.location_repo.delete_old_locations(user_id, before_time)
