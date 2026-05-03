from app.agent.tools.speech_to_text import speech_to_text
from app.agent.tools.navigation import get_destination_coordinates
from app.llmclient import text_llm
from app.services.favorite_place import FavoritePlaceService
from typing import Dict, Optional
from fastapi import UploadFile
from difflib import SequenceMatcher


class DestinationParseAgent:
    def __init__(self, favorite_place_service: Optional[FavoritePlaceService] = None):
        self.favorite_place_service = favorite_place_service

    def process_voice_input(self, audio_file: UploadFile, user_id: Optional[int] = None) -> Dict:
        try:
            voice_text = speech_to_text(audio_file)
            if voice_text == "ASR Error":
                return {"voice_text": "", "destination": "", "error": "语音解析失败"}

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
        matched_result = self._match_favorite_place(text, user_id)
        if matched_result:
            return matched_result

        matched_result = self._match_with_amap(text)
        if matched_result and "error" not in matched_result:
            return matched_result

        return self._parse_with_llm(text)

    # TODO 待优化成利用llm进行匹配
    def _match_favorite_place(self, text: str, user_id: Optional[int]) -> Optional[Dict]:
        if not user_id or not self.favorite_place_service:
            return None

        try:
            favorite_places = self.favorite_place_service.get_active_places(user_id)
            if not favorite_places:
                return None

            best_match = None
            highest_score = 0.6

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
            prompt = f"请从以下老年人的口语化表达中提取目的地信息，只返回目的地名称或地址，不要包含其他内容：{text}"

            response = text_llm.invoke(prompt)

            destination = response.content.strip()
            destination = destination.replace("。", "").replace(".", "").strip()

            return {
                "address": destination,
                "latitude": None,
                "longitude": None,
                "matched_type": "llm"
            }
        except Exception as e:
            return {
                "address": text,
                "latitude": None,
                "longitude": None,
                "matched_type": "llm"
            }