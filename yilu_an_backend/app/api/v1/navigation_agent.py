from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.agent.navigation_agent import NavigationAgent
from app.dependencies import get_navigation_agent
from typing import Dict

router = APIRouter()

@router.post("/process-voice")
async def process_voice(
    audio_file: UploadFile = File(...),
    agent: NavigationAgent = Depends(get_navigation_agent)
) -> Dict:
    """处理语音输入并规划导航路线

    - audio_file: 音频文件
    """
    try:
        # 处理语音输入并规划路线
        result = await agent.process_voice_input(audio_file)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理语音输入失败: {str(e)}"
        )

@router.post("/process-text")
async def process_text(
    text: str,
    agent: NavigationAgent = Depends(get_navigation_agent)
) -> Dict:
    """处理文本输入并规划导航路线

    - text: 文本输入
    """
    try:
        # 解析目的地
        destination = agent.destination_agent._parse_destination(text)
        if not destination:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法从文本中提取目的地信息"
            )

        # 获取当前位置
        current_location = await agent._get_current_location()

        # 规划路线
        route_data = await agent.navigation_service.plan_route(
            origin=current_location,
            destination=destination,
            priority="elderly_friendly"
        )

        # 整理路线数据
        formatted_route = agent._format_route_data(route_data)

        return {
            "voice_text": text,
            "destination": destination,
            "route": formatted_route
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理文本输入失败: {str(e)}"
        )