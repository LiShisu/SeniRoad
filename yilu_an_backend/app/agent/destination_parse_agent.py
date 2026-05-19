from app.agent.tools.speech_to_text import process_speech_to_text
from app.agent.tools.navigation import get_destination_coordinates
from app.llmclient import text_llm
from app.services.favorite_place import FavoritePlaceService
from typing import Dict, Optional
from fastapi import UploadFile
from difflib import SequenceMatcher

# 废弃，使用workflow.py中的destination_parse_node.py
class DestinationParseAgent:
    def __init__(self, favorite_place_service: Optional[FavoritePlaceService] = None):
        self.favorite_place_service = favorite_place_service

    async def process_voice_input(self, audio_file: UploadFile, user_id: Optional[int] = None) -> Dict:
        try:
            voice_text = await process_speech_to_text(audio_file)
            if "Error" in voice_text or voice_text == "ASR Error":
                return {"voice_text": "", "destination": "", "error": f"语音解析失败: {voice_text}"}

            #按照：LLM提取 -> 收藏夹匹配 -> 高德匹配 的顺序
            destination_info = self._parse_destination(voice_text, user_id)

            return {
                "voice_text": voice_text,
                "destination": destination_info.get("address", voice_text),
                "latitude": destination_info.get("latitude"),
                "longitude": destination_info.get("longitude"),
                "matched_type": destination_info.get("matched_type", "llm")
            }
        except Exception as e:
            return {"voice_text": "", "destination": "", "error": str(e)}

    def _parse_destination(self, text: str, user_id: Optional[int] = None) -> Dict:
        # 第一步：LLM 剔除口语废话，提取核心地名
        llm_result = self._parse_with_llm(text)
        core_destination = llm_result.get("address", text)

        # 第二步：使用干净的地名去匹配收藏夹
        matched_result = self._match_favorite_place(core_destination, user_id)
        if matched_result:
            return matched_result

        # 第三步：收藏夹没有，去高德搜索经纬度
        matched_result = self._match_with_amap(core_destination)
        if matched_result and "error" not in matched_result:
            return matched_result

        # 如果连高德都找不到，返回仅有的文本信息（通常会在后续逻辑报错抛出）
        return llm_result

    def _match_favorite_place(self, text: str, user_id: Optional[int]) -> Optional[Dict]:
        if not user_id or not self.favorite_place_service:
            return None
        try:
            favorite_places = self.favorite_place_service.get_active_places(user_id)
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
        except Exception as e:
            return None

    def _match_with_amap(self, text: str) -> Optional[Dict]:
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
        except Exception as e:
            return None

    def _parse_with_llm(self, text: str) -> Dict:
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
        