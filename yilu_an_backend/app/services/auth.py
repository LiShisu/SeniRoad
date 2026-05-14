from app.utils.security import create_access_token
from app.utils.validators import validate_phone
from app.repositories.user_repository import UserRepository
from app.models import User, UserRole
from app.schemas.user import LoginResponse, WechatUserCreate
from fastapi import HTTPException, status
import httpx
from app.config import settings
from app.schemas.exception import BusinessException, UnauthorizedException, NotFoundException
class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def wechat_register(self, wechat_data: WechatUserCreate):
        if not validate_phone(wechat_data.phone):
            raise BusinessException(code=400, message="手机号格式不正确")

        if self.user_repository.exists_by_phone(wechat_data.phone):
            raise BusinessException(code=400, message="该手机号已注册")

        result = await get_wechat_openid_session_key(wechat_data.code)

        openid = result.get("openid")
        db_user = User(
            phone=wechat_data.phone,
            openid=openid,
            nickname=wechat_data.nickname,
            role=wechat_data.role,
            is_active=True
        )

        self.user_repository.create(db_user)

        # 【修改点】：Service 层完成任务即可，不需要返回 {"message": "Registration successful"}
        # 返回提示信息是 API 层（Result）的职责
        return None

    async def wechat_login(self, code: str, role: UserRole) -> LoginResponse:
        result = await get_wechat_openid_session_key(code)

        openid = result.get("openid")
        user = self.user_repository.get_by_openid_and_role(openid, role)
        if not user:
            raise UnauthorizedException(message="未找到该用户，请先注册")

        access_token = create_access_token(
            data={"sub": str(user.user_id)}
        )

        return LoginResponse(access_token=access_token, role=user.role)

    async def phone_login(self, phone: str) -> LoginResponse:
        if not validate_phone(phone):
            raise BusinessException(code=400, message="手机号格式不正确")

        user = self.user_repository.get_by_phone(phone)
        if not user:
            raise UnauthorizedException(message="未找到该用户，请先注册")

        if not user.is_active:
            raise UnauthorizedException(message="该用户账号已被禁用")

        access_token = create_access_token(
            data={"sub": str(user.user_id)}
        )

        return LoginResponse(access_token=access_token, role=user.role)


async def get_wechat_openid_session_key(code: str) -> dict:
    wechat_api_url = settings.WECHAT_API_URL
    params = {
        "appid": settings.WECHAT_APPID,
        "secret": settings.WECHAT_APPSECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(wechat_api_url, params=params)
        result = response.json()

    if "errcode" in result and result["errcode"] != 0:
        raise UnauthorizedException(message=f"微信登录验证失败: {result.get('errmsg', '未知错误')}")

    openid = result.get("openid")
    session_key = result.get("session_key")

    if not openid or not session_key:
        raise UnauthorizedException(message="无法从微信服务器获取身份标识")
    return {"openid": openid, "session_key": session_key}
