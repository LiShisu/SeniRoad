from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db

from app.repositories.navigation_record_repository import NavigationRecordRepository
from app.repositories.voice_log_repository import VoiceLogRepository
from app.repositories.user_repository import UserRepository
from app.repositories.binding_repository import BindingRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.favorite_place_repository import FavoritePlaceRepository
from app.services.navigation_record import NavigationRecordService
from app.services.voice_log import VoiceLogService
from app.services.user import UserService
from app.services.navigation import NavigationService
from app.services.favorite_place import FavoritePlaceService
from app.services.location import LocationService
from app.agent.navigation_agent import NavigationAgent
from app.agent.destination_parse_agent import DestinationParseAgent
from app.agent.llm_navigation_agent import LLMNavigationAgent


def get_navigation_record_repository(db: Session = Depends(get_db)):
    return NavigationRecordRepository(db)

def get_navigation_record_service(db: Session = Depends(get_db)):
    return NavigationRecordService(db)

def get_voice_log_repository(db: Session = Depends(get_db)):
    return VoiceLogRepository(db)

def get_voice_log_service(db: Session = Depends(get_db)):
    return VoiceLogService(db)

def get_favorite_place_repository(db: Session = Depends(get_db)):
    return FavoritePlaceRepository(db)

def get_favorite_place_service(db: Session = Depends(get_db)):
    return FavoritePlaceService(db)

def get_navigation_service():
    return NavigationService()

def get_destination_parse_agent():
    return DestinationParseAgent()

def get_navigation_agent(
    navigation_service: NavigationService = Depends(get_navigation_service),
    destination_agent: DestinationParseAgent = Depends(get_destination_parse_agent)
):
    return NavigationAgent(navigation_service, destination_agent)

def get_llm_navigation_agent():
    return LLMNavigationAgent()

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)):
    return UserService(user_repo)

def get_binding_repository(db: Session = Depends(get_db)):
    return BindingRepository(db)

def get_location_repository(db: Session = Depends(get_db)):
    return LocationRepository(db)

def get_location_service(db: Session = Depends(get_db)):
    return LocationService(db)
