from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.agent.navigation_agent import NavigationAgent
from app.dependencies import get_ai_parser_service, get_navigation_service
from app.services.ai_parser import AIParserService
from app.services.navigation import NavigationService
from typing import Dict
import os
import tempfile

router = APIRouter()

@router.post("/process-voice")
async def process_voice(
    audio_file: UploadFile = File(...),
    ai_parser_service: AIParserService = Depends(get_ai_parser_service),
    navigation_service: NavigationService = Depends(get_navigation_service)
) -> Dict:
    """处理语音输入并规划导航路线
    
    - audio_file: 音频文件
    """
    try:
        # 保存上传的音频文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # 初始化导航agent
        agent = NavigationAgent(ai_parser_service, navigation_service)
        
        # 处理语音输入并规划路线
        result = await agent.process_voice_input(temp_file_path)
        
        # 删除临时文件
        os.unlink(temp_file_path)
        
        return result
    except Exception as e:
        # 确保临时文件被删除
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理语音输入失败: {str(e)}"
        )

@router.post("/process-text")
async def process_text(
    text: str,
    ai_parser_service: AIParserService = Depends(get_ai_parser_service),
    navigation_service: NavigationService = Depends(get_navigation_service)
) -> Dict:
    """处理文本输入并规划导航路线
    
    - text: 文本输入
    """
    try:
        # 初始化导航agent
        agent = NavigationAgent(ai_parser_service, navigation_service)
        
        # 模拟语音转文本的结果
        voice_text = text
        
        # 提取目的地信息
        destination_info = await ai_parser_service.parse_destination(voice_text)
        if not destination_info or "destination" not in destination_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法从文本中提取目的地信息"
            )
        
        destination = destination_info["destination"]
        
        # 获取当前位置
        current_location = await agent._get_current_location()
        
        # 规划路线
        route_data = await navigation_service.plan_route(
            origin=current_location,
            destination=destination,
            priority="elderly_friendly"
        )
        
        # 整理路线数据
        formatted_route = agent._format_route_data(route_data)
        
        return {
            "voice_text": voice_text,
            "destination": destination,
            "route": formatted_route
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理文本输入失败: {str(e)}"
        )
