from fastapi import APIRouter, Depends
from app.services.auth import AuthService
from app.schemas.user import LoginResponse, WechatUserCreate, WechatLoginRequest, PhoneLoginRequest
from app.dependencies import get_auth_service
from app.middleware.logging import logger
from app.schemas.base import Result
from typing import Any

router = APIRouter()

@router.post("/register/wechat",response_model=Result[None])
async def wechat_register(wechat_data: WechatUserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """微信小程序用户注册"""
    await auth_service.wechat_register(wechat_data)
    # API 层负责将成功的状态包装到 Result 中
    return Result(code=200, message="微信方式注册成功")

@router.post("/login/wechat", response_model=Result[LoginResponse])
async def wechat_login(login_data: WechatLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """微信小程序用户登录"""
    logger.info(f"wechat_login code: {login_data.code}, role: {login_data.role}")
    token_data = await auth_service.wechat_login(login_data.code, login_data.role)
    # API 层负责将 token 数据包装到 Result 中返回
    return Result(code=200, message="微信方式登录成功", data=token_data)

@router.post("/login/phone", response_model=Result[LoginResponse])
async def phone_login(login_data: PhoneLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    token_data = await auth_service.phone_login(login_data.phone)
    # 同上，包装 Result
    return Result(code=200, message="手机号方式登录成功", data=token_data)
