# 依赖注入函数目录
# 包含应用中使用的依赖注入函数
# 负责业务逻辑相关的依赖注入

from app.dependencies.auth import (
    get_current_user, 
    get_current_active_user, 
    get_user_repository,
    get_auth_service,
    get_user_service
)
from app.utils.security import create_access_token
from app.dependencies.services import (
    get_device_repository,
    get_device_service,
    get_navigation_record_repository,
    get_navigation_record_service,
    get_voice_log_repository,
    get_voice_log_service,
    get_ai_parser_service,
    get_navigation_service
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "create_access_token",
    "get_user_repository",
    "get_auth_service",
    "get_user_service",
    "get_device_repository",
    "get_device_service",
    "get_navigation_record_repository",
    "get_navigation_record_service",
    "get_voice_log_repository",
    "get_voice_log_service",
    "get_ai_parser_service",
    "get_navigation_service"
]

