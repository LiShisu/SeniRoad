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
        """微信小程序用户注册"""
        # 验证手机号格式
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, wechat_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
        
        # 检查手机号是否已存在
        if self.user_repository.exists_by_phone(wechat_data.phone):
            # 如果手机号已存在，返回现有用户
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        
        result = await get_wechat_openid_session_key(wechat_data.code)
        
        openid = result.get("openid")
        session_key = result.get("session_key")

        role = UserRole.ELDERLY if wechat_data.role == "elderly" else UserRole.FAMILY
        # 创建新用户
        db_user = User(
            phone=wechat_data.phone,
            openid=openid,
            session_key=session_key,
            nickname=wechat_data.nickname,
            role=role,
            is_active=True
        )

        # 保存用户
        self.user_repository.create(db_user)
        
        return {"message": "Registration successful"}
    
    async def wechat_login(self, code: str) -> LoginResponse:
        """微信小程序用户登录"""
        
        # 获取openid和session_key
        result = await get_wechat_openid_session_key(code)
        
        openid = result.get("openid")
        session_key = result.get("session_key")
        
        # 查找用户
        user = self.user_repository.get_by_openid(openid)
        if not user:
            # 用户不存在，返回错误
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 更新session_key
        user.session_key = session_key
        self.user_repository.update(user)
        
        # 生成访问令牌
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        
        return LoginResponse(access_token=access_token, role=user.role)

async def get_wechat_openid_session_key(code: str) -> dict:
    """获取微信小程序用户openid和session_key"""
    # 向微信服务器换取 session_key 和 openid
    wechat_api_url = settings.WECHAT_API_URL
    params = {
        "appid": settings.WECHAT_APPID,  # 需要在配置中添加
        "secret": settings.WECHAT_APPSECRET,  # 需要在配置中添加
        "js_code": code,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(wechat_api_url, params=params)
        result = response.json()
    
    # 检查微信API返回结果
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
