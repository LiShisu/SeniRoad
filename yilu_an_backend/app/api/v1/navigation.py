from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.dependencies.services import get_navigation_service_agent
from app.services.navigation import NavigationService
from app.agent.destination_parse_agent import DestinationParseAgent
from app.dependencies import get_current_active_user, get_navigation_service, get_voice_log_service
from app.models import User
from app.schemas.navigation import NavigationPlanRequest, NavigationPlanResponse
from typing import Dict

router = APIRouter()

@router.post("/process",tags=["语音导航"])
async def process_audio(
    audio_file: UploadFile = File(...),
    origin_lng: str = None,
    origin_lat: str = None,
    navigation_service: NavigationService = Depends(get_navigation_service_agent),
    current_user: User = Depends(get_current_active_user)
) -> Dict:
    return await navigation_service.process_voice_navigation(
        audio_file=audio_file,
        user_id=current_user.user_id,
        origin_lng=origin_lng,
        origin_lat=origin_lat
    )

@router.post("/plan",tags=["id导航"])
async def plan_route(
    request: NavigationPlanRequest,
    current_user: User = Depends(get_current_active_user),
    navigation_service: NavigationService = Depends(get_navigation_service_agent),
):
    return await navigation_service.process_text_navigation(
        origin_lng=request.origin_lng,
        origin_lat=request.origin_lat,
        favorite_place_id=request.favorite_place_id,
        user_id=current_user.user_id
    )

@router.post("/", response_model=NavigationPlanResponse, tags=["地址导航"])
async def plan_route(
    request: NavigationPlanRequest,
    current_user: User = Depends(get_current_active_user),
    navigation_service: NavigationService = Depends(get_navigation_service),
):
    return await navigation_service.plan(
        favorite_place_id=request.favorite_place_id,
        origin_lng=request.origin_lng,
        origin_lat=request.origin_lat,
        user_id=current_user.user_id
    )
