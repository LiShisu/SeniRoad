from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .binding import router as binding_router
from .location import router as location_router
from .destination import router as destination_router
from .navigation import router as navigation_router
from .device import router as device_router
from .navigation_record import router as navigation_record_router
from .voice_log import router as voice_log_router
from .navigation_agent import router as navigation_agent_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["认证"])
router.include_router(user_router, prefix="/users", tags=["用户"])
router.include_router(binding_router, prefix="/bindings", tags=["绑定"])
router.include_router(location_router, prefix="/locations", tags=["位置"])
router.include_router(destination_router, prefix="/destinations", tags=["目的地"])
router.include_router(navigation_router, prefix="/navigation", tags=["导航"])
router.include_router(device_router, prefix="/devices", tags=["设备"])
router.include_router(navigation_record_router, prefix="/navigation-records", tags=["导航记录"])
router.include_router(voice_log_router, prefix="/voice-logs", tags=["语音日志"])
router.include_router(navigation_agent_router, prefix="/navigation-agent", tags=["导航Agent"])
