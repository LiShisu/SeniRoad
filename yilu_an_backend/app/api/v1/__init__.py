from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .binding import router as binding_router
from .location import router as location_router
from .favorite_place import router as favorite_place_router
from .tag import router as tag_router

from .navigation import router as navigation_router
from .navigation_record import router as navigation_record_router
from .voice_log import router as voice_log_router
from .navigation_agent import router as navigation_agent_router
from .llm_navigation_agent import router as llm_navigation_agent_router
from .speech_to_text import router as speech_to_text_router
# from .views import router as views_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["认证"])
router.include_router(user_router, prefix="/users", tags=["用户"])
router.include_router(binding_router, prefix="/bindings", tags=["绑定"])
router.include_router(location_router, prefix="/locations", tags=["位置"])
router.include_router(favorite_place_router, prefix="/favorite-places", tags=["收藏地点"])
router.include_router(tag_router, prefix="/tags", tags=["标签"])

router.include_router(navigation_router, prefix="/navigation", tags=["导航"])
router.include_router(voice_log_router, prefix="/voice-logs", tags=["语音日志"])
# router.include_router(navigation_agent_router, prefix="/navigation-agent", tags=["导航Agent"])
router.include_router(llm_navigation_agent_router, prefix="/llm-navigation-agent", tags=["LLM导航Agent"])
router.include_router(speech_to_text_router, prefix="/speech", tags=["语音处理"])
# router.include_router(views_router, prefix="/views", tags=["视图"])
