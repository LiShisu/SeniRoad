from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.agent.llm_navigation_agent import LLMNavigationAgent
from app.dependencies import get_llm_navigation_agent
from typing import Dict

router = APIRouter()

# 废弃
@router.post("/process-voice")
async def process_voice(
    audio_file: UploadFile = File(...),
    current_location: str = None,
    agent: LLMNavigationAgent = Depends(get_llm_navigation_agent)
) -> Dict:
    """处理语音输入并规划导航路线（使用LLM）

    - audio_file: 音频文件
    - current_location: 当前位置坐标，格式为"经度,纬度"，由前端传入
    """
    try:
        # 处理语音输入并规划路线
        result = await agent.process_input(audio_file=audio_file, current_location=current_location)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理语音输入失败: {str(e)}"
        )

@router.post("/process-text")
async def process_text(
    text: str,
    current_location: str = None,
    agent: LLMNavigationAgent = Depends(get_llm_navigation_agent)
) -> Dict:
    """处理文本输入并规划导航路线（使用LLM）

    - text: 文本输入
    - current_location: 当前位置坐标，格式为"经度,纬度"，由前端传入
    """
    try:
        # 处理文本输入并规划路线
        result = await agent.process_input(input_data=text, current_location=current_location)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理文本输入失败: {str(e)}"
        )