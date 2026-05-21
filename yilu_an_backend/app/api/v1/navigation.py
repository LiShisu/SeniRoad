from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File,Form
from fastapi.responses import StreamingResponse
from app.dependencies.services import get_navigation_service_agent
from app.services.navigation import NavigationService
from app.dependencies import get_current_active_user, get_navigation_service
from app.models import User
# from app.schemas.navigation import NavigationPlanRequest, NavigationPlanResponse
from typing import Dict
from app.schemas.navigation import (
    NavigationPlanRequest, 
    NavigationPlanResponse,
    SmartNavigationResponse,
    VoiceNavigationResponse,
    CoordinateNavRequest,
    NavigationRoute,
)
from app.schemas.base import Result
router = APIRouter()
# 3. 语音智能导航
@router.post("/routes/voice", response_model=Result[VoiceNavigationResponse], status_code=status.HTTP_201_CREATED, tags=["语音导航路线"])
async def create_voice_route(
    audio_file: UploadFile = File(...),
    origin_lng: str = None,
    origin_lat: str = None,
    navigation_service: NavigationService = Depends(get_navigation_service_agent),
    current_user: User = Depends(get_current_active_user)
) :
    """创建语音导航路线 (自动解析语音目的地)"""
    data = navigation_service.process_voice_navigation(
        audio_file=audio_file,
        user_id=current_user.user_id,
        origin_lng=origin_lng,
        origin_lat=origin_lat
    )
    return Result(code=200, message="语音路线解析成功", data=data)

@router.post("/routes/voice/stream", tags=["语音导航-SSE"])
async def create_voice_route_stream(
    audio_file: UploadFile = File(...),
    origin_lat: str = Form(..., description="起点纬度"),
    origin_lng: str = Form(..., description="起点经度"),
    # 🌟 核心修改 1：通过 Form 接收多模态参数，并给定默认值向下兼容
    travel_mode: str = Form("walking", description="出行方式(walking/transit)"),
    city: str = Form("济南市", description="当前城市"),
    navigation_service: NavigationService = Depends(get_navigation_service_agent),
    current_user: User = Depends(get_current_active_user)
):
    """SSE 流式语音导航接口"""
    return StreamingResponse(
        navigation_service.process_voice_navigation_stream(
            audio_file=audio_file,
            user_id=current_user.user_id,
            origin_lng=origin_lng,
            origin_lat=origin_lat,
            travel_mode=travel_mode,  # 🌟 核心修改 2：透传给 Service
            city=city                 # 🌟 核心修改 2：透传给 Service
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
# 2. 智能文本导航 (大模型)
@router.post("/routes/smart", response_model=Result[SmartNavigationResponse], status_code=status.HTTP_201_CREATED, tags=["智能导航路线"])
async def create_smart_route(
    request: NavigationPlanRequest,
    current_user: User = Depends(get_current_active_user),
    navigation_service: NavigationService = Depends(get_navigation_service_agent),
):
    """创建智能导航路线 (结合大模型天气与出行建议)"""
    data = await navigation_service.process_text_navigation(
        origin_lng=request.origin_lng,
        origin_lat=request.origin_lat,
        favorite_place_id=request.favorite_place_id,
        user_id=current_user.user_id
    )
    return Result(code=200, message="智能路线生成成功", data=data)

@router.post("/routes/smart/stream", tags=["智能导航-SSE"])
async def create_smart_route_stream(
    request: NavigationPlanRequest,
    current_user: User = Depends(get_current_active_user),
    navigation_service: NavigationService = Depends(get_navigation_service_agent),
):
    print(f"前端传入的 travel_mode: {request.travel_mode}")
    print(f"前端传入的 city:        {request.city}")
    """SSE 流式导航接口 - 分阶段返回数据，避免前端超时
    
    返回事件类型:
    - start: 开始处理
    - destination: 目的地信息
    - route: 路线规划完成
    - weather: 天气信息
    - advice: 出行建议
    - complete: 所有数据发送完毕
    - error: 发生错误
    """
    return StreamingResponse(
        navigation_service.process_text_navigation_stream(
            origin_lng=request.origin_lng,
            origin_lat=request.origin_lat,
            favorite_place_id=request.favorite_place_id,
            user_id=current_user.user_id,
            travel_mode=request.travel_mode, # 👈 必须加上
            city=request.city
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# 1. 标准地址导航 (纯高德路线规划)
@router.post("/routes/standard", response_model=Result[NavigationPlanResponse], status_code=status.HTTP_201_CREATED, tags=["基础导航路线"])
async def create_standard_route(
    request: NavigationPlanRequest,
    current_user: User = Depends(get_current_active_user),
    navigation_service: NavigationService = Depends(get_navigation_service),
):
    """创建标准导航路线 (基于纯高德API)"""
    data = await navigation_service.plan(
        favorite_place_id=request.favorite_place_id,
        origin_lng=request.origin_lng,
        origin_lat=request.origin_lat,
        user_id=current_user.user_id
    )
    return Result(code=200, message="标准路线(基于纯高德API)规划成功", data=data)

@router.post("/routes/coordinates", response_model=Result[NavigationRoute])
async def navigate_by_coordinates(
    req: CoordinateNavRequest,
    current_user = Depends(get_current_active_user) ,
    navigation_service: NavigationService = Depends(get_navigation_service),
):
    try:
        route_data = await navigation_service.get_fast_amap_route(
            origin_lng=req.origin_lng,
            origin_lat=req.origin_lat,
            dest_lng=req.dest_lng,
            dest_lat=req.dest_lat
        )
        if not route_data:
            return Result(
                code=500, 
                message="语音重新规划：重新规划规划失败", 
                data=None
            )

        # 完美对齐前端期待的数据格式
        return Result(
            code=200, 
            message="success", 
            data=route_data
        )
    except Exception as e:
        return Result(
            code=500, 
            message=f"路线重算异常: {str(e)}", 
            data=None
        )
