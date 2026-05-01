from sqlalchemy.orm import Session
from app.models.location import Location
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, location_id: int) -> Optional[Location]:
        return self.db.query(Location).filter(Location.location_id == location_id).first()

    def get_by_user_id(self, user_id: int, start_time: datetime = None, end_time: datetime = None, limit: int = 100) -> List[Location]:
        query = self.db.query(Location).filter(Location.user_id == user_id)
        if start_time:
            query = query.filter(Location.created_at >= start_time)
        if end_time:
            query = query.filter(Location.created_at <= end_time)
        return query.order_by(Location.created_at.desc()).limit(limit).all()

    def get_latest_by_user_id(self, user_id: int) -> Optional[Location]:
        return self.db.query(Location).filter(Location.user_id == user_id).order_by(Location.created_at.desc()).first()

    def get_by_time_range(self, user_id: int, start_time: datetime, end_time: datetime) -> List[Location]:
        return self.db.query(Location).filter(
            Location.user_id == user_id,
            Location.created_at >= start_time,
            Location.created_at <= end_time
        ).order_by(Location.created_at).all()

    def get_by_record_id(self, record_id: int) -> List[Location]:
        return self.db.query(Location).filter(Location.record_id == record_id).order_by(Location.created_at).all()

    def create_location(self, user_id: int, latitude: Decimal, longitude: Decimal, address: Optional[str] = None, accuracy: Optional[float] = None, record_id: Optional[int] = None) -> Location:
        location = Location(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            address=address,
            accuracy=accuracy,
            record_id=record_id
        )
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def create(self, location: Location) -> Location:
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def bulk_create(self, locations: List[Location]) -> List[Location]:
        self.db.add_all(locations)
        self.db.commit()
        for location in locations:
            self.db.refresh(location)
        return locations

    def delete_old_locations(self, user_id: int, before_time: datetime) -> int:
        deleted = self.db.query(Location).filter(
            Location.user_id == user_id,
            Location.created_at < before_time
        ).delete()
        self.db.commit()
        return deleted
