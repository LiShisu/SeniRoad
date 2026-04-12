from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import AuthService
from app.schemas.user import UserCreate, UserResponse, LoginResponse, WechatUserCreate
from app.dependencies import get_auth_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """用户注册"""
    return await auth_service.register(user)

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    """用户登录"""
    return await auth_service.login(form_data.username, form_data.password)

@router.post("/wechat/register", response_model=UserResponse)
async def wechat_register(wechat_data: WechatUserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """微信小程序用户注册"""
    return await auth_service.wechat_register(wechat_data)

@router.post("/wechat/login", response_model=LoginResponse)
async def wechat_login(openid: str, session_key: str, auth_service: AuthService = Depends(get_auth_service)):
    """微信小程序用户登录"""
    return await auth_service.wechat_login(openid, session_key)
