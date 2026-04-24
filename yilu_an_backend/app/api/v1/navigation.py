from fastapi import APIRouter, Depends, HTTPException, status
from app.services.navigation import NavigationService
from app.services.ai_parser import AIParserService
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
    ai_parser: AIParserService = Depends()
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
        
        # 如果目的地是名称，尝试解析
        if not "," in destination:
            parsed_result = await ai_parser.parse_destination(destination)
            # 这里需要根据实际的AI解析结果格式进行处理
            # 暂时假设解析结果包含坐标
            destination = "116.397428,39.90923"
        
        route_data = await nav_service.plan_route(origin, destination, priority)
        return route_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"规划路线失败: {str(e)}"
        )
