"""
目的地解析节点

负责解析用户输入的目的地，支持：
1. 语音转文本
2. LLM提取核心地名
3. 收藏夹匹配
4. 高德关键词匹配
"""

import json
from typing import Optional, Dict
from fastapi import UploadFile
from difflib import SequenceMatcher

from pydantic.types import T
from app.agent.schemas import NavigationWorkflowState
from app.llmclient import text_llm
from app.agent.tools.speech_to_text import process_speech_to_text
from app.agent.tools.amap_tools import AmapApiTools
from app.services.favorite_place import FavoritePlaceService
import logging
logger = logging.getLogger(__name__)
TEST = False

async def destination_parse_node(
    state: NavigationWorkflowState,
    favorite_place_service: Optional[FavoritePlaceService] = None
) -> dict:
    """目的地解析节点

    根据输入类型（语音/文本/favorite_place_id）解析目的地。

    Args:
        state: 当前工作流状态
        favorite_place_service: 收藏地点服务（可选）

    Returns:
        dict: 更新后的状态字段
    """
    logger.info(f"[DEBUG] destination_parse_node: state.city = {repr(state.city)}, origin_lng={state.origin_lng}, origin_lat={state.origin_lat}")
    # 如果提供了favorite_place_id，直接从收藏夹获取
    if state.favorite_place_id and favorite_place_service:
        return _parse_from_favorite(state.favorite_place_id, favorite_place_service)

    # 如果提供了音频文件，先进行语音转文本
    if TEST:
        voice_text = "我想去大明湖"
    else:
        voice_text = state.voice_text
    logger.info(f"原始语音文本: {voice_text}")

    if state.audio_file and not voice_text:
        voice_text = await process_speech_to_text(state.audio_file)
        if "Error" in voice_text or voice_text == "ASR Error":
            return {
                "voice_text": "",
                "destination_name": "",
                "destination_lng": None,
                "destination_lat": None,
                "matched_type": "error"
            }

    # 按照：LLM提取 -> 收藏夹匹配 -> 高德匹配 的顺序（传递city参数以提高高德查询准确性）
    destination_info = await _parse_destination_text(
        voice_text,
        state.user_id,
        favorite_place_service,
        state.city,
        state.origin_lng,
        state.origin_lat
    )

    return {
        "voice_text": voice_text,
        "destination_name": destination_info.get("address", voice_text),
        "destination_lng": destination_info.get("longitude"),
        "destination_lat": destination_info.get("latitude"),
        "matched_type": destination_info.get("matched_type", "llm")
    }


def _parse_from_favorite(
    favorite_place_id: int,
    favorite_place_service: FavoritePlaceService
) -> dict:
    """从收藏夹获取目的地"""
    favorite_place = favorite_place_service.get_place_by_id(favorite_place_id)
    if not favorite_place:
        return {
            "destination_name": "",
            "destination_lng": None,
            "destination_lat": None,
            "matched_type": "error"
        }

    return {
        "destination_name": favorite_place.place_name,
        "destination_lng": str(favorite_place.longitude),
        "destination_lat": str(favorite_place.latitude),
        "matched_type": "favorite"
    }


async def _parse_destination_text(
    text: str,
    user_id: Optional[int],
    favorite_place_service: Optional[FavoritePlaceService],
    city: Optional[str] = None,
    origin_lng: Optional[str] = None,
    origin_lat: Optional[str] = None
) -> Dict:
    """解析文本中的目的地

    按照：LLM提取 -> 收藏夹匹配 -> 高德匹配 的顺序
    """
    logger.info(f"[DEBUG] _parse_destination_text: city = {repr(city)}, origin_lng={origin_lng}, origin_lat={origin_lat}")
    # 第一步：LLM 剔除口语废话，提取核心地名
    if TEST:
        # 测试模式下直接返回原始文本
        llm_result = {"address": "大明湖"}
    else:
        # 正常模式下调用LLM
        llm_result = _parse_with_llm(text)
    core_destination = llm_result.get("address", text)
    logger.info(f"LLM提取的核心地名: {core_destination}")

    # 第二步：使用干净的地名去匹配收藏夹
    matched_result = _match_favorite_place(core_destination, user_id, favorite_place_service)
    if matched_result:
        return matched_result

    # 第三步：收藏夹没有，去高德搜索经纬度（传递city参数以提高准确性）
    matched_result = await _match_with_amap(core_destination, city, origin_lng, origin_lat)
    if matched_result and "error" not in matched_result:
        return matched_result

    # 如果连高德都找不到，返回仅有的文本信息
    return llm_result


def _match_favorite_place(
    text: str,
    user_id: Optional[int],
    favorite_place_service: Optional[FavoritePlaceService]
) -> Optional[Dict]:
    """匹配收藏夹中的地点"""
    if not user_id or not favorite_place_service:
        return None
    try:
        favorite_places = favorite_place_service.get_active_places(user_id)
        if not favorite_places:
            return None

        best_match = None
        highest_score = 0.8

        text_lower = text.lower()
        for place in favorite_places:
            place_name_lower = place.place_name.lower()
            address_lower = place.address.lower()

            name_score = SequenceMatcher(None, text_lower, place_name_lower).ratio()
            addr_score = SequenceMatcher(None, text_lower, address_lower).ratio()
            combined_score = max(name_score, addr_score)

            if combined_score > highest_score:
                highest_score = combined_score
                best_match = place

        if best_match:
            return {
                "address": best_match.place_name,
                "latitude": float(best_match.latitude),
                "longitude": float(best_match.longitude),
                "matched_type": "favorite"
            }
        return None
    except Exception:
        return None


async def _match_with_amap(text: str, city: Optional[str] = None, 
                           origin_lng: Optional[str] = None,
                           origin_lat: Optional[str] = None) -> Optional[Dict]:
    """使用高德API匹配地点

    Args:
        text: 目的地名称或地址
        city: 城市名称（可选），用于提高查询准确性
        origin_lng: 起点经度（可选），用于从坐标反查城市
        origin_lat: 起点纬度（可选），用于从坐标反查城市
    """
    logger.info(f"[DEBUG] _match_with_amap: text = {repr(text)}, city = {repr(city)}, origin_lng={origin_lng}, origin_lat={origin_lat}")
    
    resolved_city = city
    
    # 1. 检查城市名是否有效
    if city:
        if len(city) == 1:
            logger.warning(f"城市名称过短: '{city}'，可能被截断了，尝试从起点坐标反查")
            resolved_city = None
        elif len(city) < 2:
            logger.warning(f"城市名称异常: '{city}'，尝试从起点坐标反查")
            resolved_city = None
    
    # 2. 如果城市名无效但有起点坐标，从坐标反查
    if not resolved_city and origin_lng and origin_lat:
        try:
            logger.info(f"尝试从起点坐标 ({origin_lng}, {origin_lat}) 反查城市名...")
            resolved_city = await AmapApiTools.get_city_by_location(origin_lng, origin_lat)
            if resolved_city:
                logger.info(f"成功从坐标反查到城市: '{resolved_city}'")
            else:
                logger.info(f"坐标反查城市失败，继续不使用城市参数")
        except Exception as e:
            logger.error(f"从坐标反查城市时出错: {e}")
    
    # 3. 尝试用最佳的城市参数搜索
    try:
        result = await AmapApiTools.get_destination_coordinates(text, resolved_city)
        logger.info(f"[DEBUG] _match_with_amap: result = {repr(result)}")
        
        # 如果搜索失败且有备选城市参数，再尝试
        if (not result or "error" in result) and resolved_city and resolved_city != city:
            logger.info(f"使用反查到的城市 '{resolved_city}' 搜索失败，尝试不带城市重新搜索...")
            result = await AmapApiTools.get_destination_coordinates(text, None)
            logger.info(f"[DEBUG] _match_with_amap (无城市重新搜索): result = {repr(result)}")
        elif (not result or "error" in result) and city and len(city) >= 2:
            logger.info(f"使用城市 '{city}' 搜索失败，尝试不带城市重新搜索...")
            result = await AmapApiTools.get_destination_coordinates(text, None)
            logger.info(f"[DEBUG] _match_with_amap (无城市重新搜索): result = {repr(result)}")
            
        if result and "error" not in result:
            return {
                "address": result.get("formatted_address", text),
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "matched_type": "amap"
            }
        return None
    except Exception as e:
        logger.error(f"高德API调用异常: {e}")
        return None


def _parse_with_llm(text: str) -> Dict:
    """使用LLM从口语化文本中提取目的地"""
    try:
        prompt = f"""
请从老年人口语化的导航诉求文本中，精准提取核心目的地名称或地址。
规则要求：
1. 只提取纯粹目的地，剔除所有多余语气词、行为描述、原因解释、闲聊无关语句；
2. 保留老人原始口语化地点表述，不改写、不精简、不补充；
3. 仅返回目的地文字，**禁止添加任何标点、禁止额外解释、禁止多余废话、禁止换行**；
4. 若语句无明确目的地，直接返回：无

示例：
输入：带我去小区门口的超市买东西
输出：小区门口的超市

输入：往人民公园走，我想去溜达溜达
输出：人民公园

输入：我想去大儿子家里
输出：大儿子家

待处理文本：{text}"""
        response = text_llm.invoke(prompt)

        destination = response.content.strip().replace("。", "").replace(".", "")
        return {
            "address": destination,
            "latitude": None,
            "longitude": None,
            "matched_type": "llm"
        }
    except Exception:
        return {"address": text, "latitude": None, "longitude": None, "matched_type": "llm"}
