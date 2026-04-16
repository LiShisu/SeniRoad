# schemas/__init__.py

from .user import (
    UserResponse,
)

from .location import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)

from .destination import (
    DestinationCreate,
    DestinationResponse,
)

from .binding import (
    BindingCreate,
    BindingResponse,
    BindingUnbind,
)

from .device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
)

from .favorite_place import (
    FavoritePlaceCreate,
    FavoritePlaceUpdate,
    FavoritePlaceResponse,
)

from .navigation_record import (
    NavigationRecordCreate,
    NavigationRecordUpdate,
    NavigationRecordResponse,
)

from .voice_log import (
    VoiceLogCreate,
    VoiceLogUpdate,
    VoiceLogResponse,
)

__all__ = [
    # User
    "UserResponse",
    # Location
    "LocationCreate",
    "LocationResponse",
    "LocationUpdate",
    # Destination
    "DestinationCreate",
    "DestinationResponse",
    # Binding
    "BindingCreate",
    "BindingResponse",
    "BindingUnbind",
    # Device
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    # FavoritePlace
    "FavoritePlaceCreate",
    "FavoritePlaceUpdate",
    "FavoritePlaceResponse",
    # NavigationRecord
    "NavigationRecordCreate",
    "NavigationRecordUpdate",
    "NavigationRecordResponse",
    # VoiceLog
    "VoiceLogCreate",
    "VoiceLogUpdate",
    "VoiceLogResponse",
]