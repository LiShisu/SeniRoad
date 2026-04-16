# models/__init__.py
from .user import User, UserRole
from .binding import Binding
from .destination import Destination
from .location import Location
from .device import Device
from .favorite_place import FavoritePlace
from .navigation_record import NavigationRecord
from .voice_log import VoiceLog

__all__ = [
    "User",
    "UserRole",
    "Binding",
    "Destination",
    "Location",
    "Device",
    "FavoritePlace",
    "NavigationRecord",
    "VoiceLog"
]
