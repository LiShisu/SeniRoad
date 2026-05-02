from fastapi import APIRouter, Depends
from app.services.auth import AuthService
from app.schemas.user import LoginResponse, WechatUserCreate, WechatLoginRequest, PhoneLoginRequest
from app.dependencies import get_auth_service
from app.middleware.logging import logger

router = APIRouter()

@router.post("/wechat/register")
async def wechat_register(wechat_data: WechatUserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """微信小程序用户注册"""
    return await auth_service.wechat_register(wechat_data)

@router.post("/wechat/login", response_model=LoginResponse)
async def wechat_login(login_data: WechatLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """微信小程序用户登录"""
    logger.info(f"wechat_login code: {login_data.code}, role: {login_data.role}")
    return await auth_service.wechat_login(login_data.code, login_data.role)

@router.post("/phone/login", response_model=LoginResponse)
async def phone_login(login_data: PhoneLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """手机号登录"""
    return await auth_service.phone_login(login_data.phone)
