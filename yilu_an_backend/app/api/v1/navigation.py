from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.services.navigation import NavigationService
from app.agent.destination_parse_agent import DestinationParseAgent
from app.dependencies import get_current_active_user, get_navigation_service, get_voice_log_service
from app.models import User
from typing import Dict

router = APIRouter()

# @router.post("/plan")
# async def plan_route(
#     request: dict,
#     current_user: User = Depends(get_current_active_user),
#     nav_service: NavigationService = Depends(get_navigation_service),
#     destination_agent: DestinationParseAgent = Depends(get_destination_parse_agent)
# ):
#     try:
#         origin = request.get("origin")
#         destination = request.get("destination")
#         priority = request.get("priority", "elderly_friendly")

#         if not origin or not destination:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="起点和终点不能为空"
#             )

#         if not "," in destination:
#             parsed_result = destination_agent.process_text_input(destination)
#             if "error" not in parsed_result:
#                 destination = parsed_result.get("destination", destination)
#             else:
#                 destination = "116.397428,39.90923"
#         else:
#             destination = "116.397428,39.90923"

#         route_data = await nav_service.plan_route(origin, destination, priority)
#         return route_data
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"规划路线失败: {str(e)}"
#         )


@router.post("/process",tags=["语音导航"])
async def process_audio(
    audio_file: UploadFile = File(...),
    origin_lng: str = None,
    origin_lat: str = None,
    navigation_service: NavigationService = Depends(get_navigation_service),
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
    favorite_place_id: int,
    origin_lng: str,
    origin_lat: str,
    current_user: User = Depends(get_current_active_user),
    navigation_service: NavigationService = Depends(get_navigation_service),
):
    return await navigation_service.process_text_navigation(
        origin_lng=origin_lng,
        origin_lat=origin_lat,
        favorite_place_id=favorite_place_id,
        user_id=current_user.user_id
    )