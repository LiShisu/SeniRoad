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
from app.agent.schemas import NavigationWorkflowState
from app.llmclient import text_llm
from app.agent.tools.speech_to_text import process_speech_to_text
from app.agent.tools.navigation import get_destination_coordinates
from app.services.favorite_place import FavoritePlaceService


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
    # 如果提供了favorite_place_id，直接从收藏夹获取
    if state.favorite_place_id and favorite_place_service:
        return _parse_from_favorite(state.favorite_place_id, favorite_place_service)

    # 如果提供了音频文件，先进行语音转文本
    voice_text = state.voice_text
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

    # 按照：LLM提取 -> 收藏夹匹配 -> 高德匹配 的顺序
    destination_info = _parse_destination_text(
        voice_text,
        state.user_id,
        favorite_place_service
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


def _parse_destination_text(
    text: str,
    user_id: Optional[int],
    favorite_place_service: Optional[FavoritePlaceService]
) -> Dict:
    """解析文本中的目的地

    按照：LLM提取 -> 收藏夹匹配 -> 高德匹配 的顺序
    """
    # 第一步：LLM 剔除口语废话，提取核心地名
    llm_result = _parse_with_llm(text)
    core_destination = llm_result.get("address", text)

    # 第二步：使用干净的地名去匹配收藏夹
    matched_result = _match_favorite_place(core_destination, user_id, favorite_place_service)
    if matched_result:
        return matched_result

    # 第三步：收藏夹没有，去高德搜索经纬度
    matched_result = _match_with_amap(core_destination)
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


def _match_with_amap(text: str) -> Optional[Dict]:
    """使用高德API匹配地点"""
    try:
        result = get_destination_coordinates.invoke({"address": text})
        if result and "error" not in result:
            return {
                "address": result.get("formatted_address", text),
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "matched_type": "amap"
            }
        return None
    except Exception:
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
