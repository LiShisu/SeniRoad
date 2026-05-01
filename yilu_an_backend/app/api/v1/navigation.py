from fastapi import APIRouter, Depends, HTTPException, status
from app.services.navigation import NavigationService
from app.agent.destination_parse_agent import DestinationParseAgent
from app.dependencies import get_current_active_user
from app.models import User
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.post("/plan")
async def plan_route(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    nav_service: NavigationService = Depends(),
    destination_agent: DestinationParseAgent = Depends()
):
    """规划导航路线
    
    - origin: 起点坐标，格式为"经度,纬度"
    - destination: 终点坐标，格式为"经度,纬度"或目的地名称
    - priority: 优先级，可选值为"elderly_friendly"（默认）、"time"、"distance"
    """
    try:
        origin = request.get("origin")
        destination = request.get("destination")
        priority = request.get("priority", "elderly_friendly")
        
        if not origin or not destination:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="起点和终点不能为空"
            )
        
        if not "," in destination:
            parsed_result = destination_agent.process_text_input(destination)
            if "error" not in parsed_result:
                destination = parsed_result.get("destination", destination)
            else:
                destination = "116.397428,39.90923"
        else:
            destination = "116.397428,39.90923"
        
        route_data = await nav_service.plan_route(origin, destination, priority)
        return route_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"规划路线失败: {str(e)}"
        )
