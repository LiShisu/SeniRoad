from app.utils.security import create_access_token
from app.repositories.user_repository import UserRepository
from app.models import User, UserRole
from app.schemas.user import LoginResponse, WechatUserCreate
from fastapi import HTTPException, status
import httpx
import re
from app.config import settings

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def wechat_register(self, wechat_data: WechatUserCreate):
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, wechat_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )

        if self.user_repository.exists_by_phone(wechat_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        result = await get_wechat_openid_session_key(wechat_data.code)

        openid = result.get("openid")

        role = UserRole.ELDERLY if wechat_data.role == "elderly" else UserRole.FAMILY

        db_user = User(
            phone=wechat_data.phone,
            openid=openid,
            nickname=wechat_data.nickname,
            role=role,
            is_active=True
        )

        self.user_repository.create(db_user)

        return {"message": "Registration successful"}

    async def wechat_login(self, code: str) -> LoginResponse:
        result = await get_wechat_openid_session_key(code)

        openid = result.get("openid")

        user = self.user_repository.get_by_openid(openid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wechat login failed: {result.get('errmsg', 'Unknown error')}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    openid = result.get("openid")
    session_key = result.get("session_key")

    if not openid or not session_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to get openid or session_key from Wechat",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"openid": openid, "session_key": session_key}
