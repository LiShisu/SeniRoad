# 数据访问层（Repositories）
# 负责封装数据库CRUD操作，与Spring Boot的Repository层对应

from app.repositories.user_repository import UserRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.destination_repository import DestinationRepository
from app.repositories.binding_repository import BindingRepository

__all__ = [
    "UserRepository",
    "LocationRepository",
    "DestinationRepository",
    "BindingRepository"
]

