# models/__init__.py
from .user import User, UserRole
from .binding import Binding
from .location import Location
from .favorite_place import FavoritePlace
from .navigation_record import NavigationRecord
from .voice_log import VoiceLog
from .tag import Tag
# from app.views.elderly_family_binding import ElderlyFamilyBindingView
# from app.views.elderly_location import ElderlyLocationView
# from app.views.elderly_favorite_places import ElderlyFavoritePlacesView
# from app.views.navigation_stats import NavigationStatsView
# from app.views.voice_interaction_logs import VoiceInteractionLogsView

__all__ = [
    "User",
    "UserRole",
    "Binding",
    "Location",
    "FavoritePlace",
    "NavigationRecord",
    "VoiceLog",
    "Tag",
    # "ElderlyFamilyBindingView",
    # "ElderlyLocationView",
    # "ElderlyFavoritePlacesView",
    # "NavigationStatsView",
    # "VoiceInteractionLogsView"
]
