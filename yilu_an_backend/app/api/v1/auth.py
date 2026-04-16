from fastapi import APIRouter, Depends
from app.services.auth import AuthService
from app.schemas.user import LoginResponse, WechatUserCreate, WechatLoginRequest
from app.dependencies import get_auth_service

router = APIRouter()

@router.post("/wechat/register")
async def wechat_register(wechat_data: WechatUserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """微信小程序用户注册"""
    return await auth_service.wechat_register(wechat_data)

@router.post("/wechat/login", response_model=LoginResponse)
async def wechat_login(login_data: WechatLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """微信小程序用户登录"""
    return await auth_service.wechat_login(login_data.code)
