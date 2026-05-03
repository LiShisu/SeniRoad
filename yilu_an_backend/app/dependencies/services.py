from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db

from app.repositories.navigation_record_repository import NavigationRecordRepository
from app.repositories.voice_log_repository import VoiceLogRepository
from app.repositories.user_repository import UserRepository
from app.repositories.binding_repository import BindingRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.favorite_place_repository import FavoritePlaceRepository
from app.repositories.tag_repository import TagRepository

from app.services.navigation_record import NavigationRecordService
from app.services.voice_log import VoiceLogService
from app.services.user import UserService
from app.services.navigation import NavigationService
from app.services.favorite_place import FavoritePlaceService
from app.services.tag import TagService
from app.services.location import LocationService
from app.services.binding import BindingService

from app.agent.navigation_agent import NavigationAgent
from app.agent.destination_parse_agent import DestinationParseAgent
from app.agent.llm_navigation_agent import LLMNavigationAgent
from app.agent.multi_agent_navigation import MultiAgentNavigation


def get_navigation_record_repository(db: Session = Depends(get_db)):
    return NavigationRecordRepository(db)

def get_navigation_record_service(
    repo: NavigationRecordRepository = Depends(get_navigation_record_repository)
):
    return NavigationRecordService(repo)

def get_voice_log_repository(db: Session = Depends(get_db)):
    return VoiceLogRepository(db)

def get_voice_log_service(
    repo: VoiceLogRepository = Depends(get_voice_log_repository)
):
    return VoiceLogService(repo)

def get_favorite_place_repository(db: Session = Depends(get_db)):
    return FavoritePlaceRepository(db)

def get_favorite_place_service(
    repo: FavoritePlaceRepository = Depends(get_favorite_place_repository)
):
    return FavoritePlaceService(repo)

def get_tag_repository(db: Session = Depends(get_db)):
    return TagRepository(db)

def get_tag_service(
    repo: TagRepository = Depends(get_tag_repository)
):
    return TagService(repo)

def get_destination_parse_agent(
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service)
):
    return DestinationParseAgent(favorite_place_service)

_navigation_service_instance = None
_multi_agent_navigation_instance = None


def get_navigation_service(
    destination_parse_agent: DestinationParseAgent = Depends(get_destination_parse_agent),
    favorite_place_service: FavoritePlaceService = Depends(get_favorite_place_service),
    navigation_record_service: NavigationRecordService = Depends(get_navigation_record_service),
    voice_log_service: VoiceLogService = Depends(get_voice_log_service)
):
    global _navigation_service_instance, _multi_agent_navigation_instance
    if _navigation_service_instance is None:
        from app.agent.multi_agent_navigation import setup_mcp_tools, create_agents
        import asyncio
        asyncio.run(setup_mcp_tools())
        create_agents()
        _multi_agent_navigation_instance = MultiAgentNavigation()
        _navigation_service_instance = NavigationService(
            destination_parse_agent=destination_parse_agent,
            favorite_place_service=favorite_place_service,
            multi_agent_navigation=_multi_agent_navigation_instance,
            navigation_record_service=navigation_record_service,
            voice_log_service=voice_log_service,
        )
    return _navigation_service_instance

def get_navigation_agent(
    navigation_service: NavigationService = Depends(get_navigation_service),
    destination_agent: DestinationParseAgent = Depends(get_destination_parse_agent)
):
    return NavigationAgent(navigation_service, destination_agent)

def get_llm_navigation_agent():
    return LLMNavigationAgent()

async def get_multi_agent_navigation():
    global _multi_agent_navigation_instance
    if _multi_agent_navigation_instance is None:
        from app.agent.multi_agent_navigation import setup_mcp_tools, create_agents
        await setup_mcp_tools()
        create_agents()
        _multi_agent_navigation_instance = MultiAgentNavigation()
    return _multi_agent_navigation_instance

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_user_service(
    repo: UserRepository = Depends(get_user_repository)
):
    return UserService(repo)

def get_binding_repository(db: Session = Depends(get_db)):
    return BindingRepository(db)

def get_binding_service(
    binding_repo: BindingRepository = Depends(get_binding_repository),
    user_repo: UserRepository = Depends(get_user_repository)
):
    return BindingService(binding_repo, user_repo)

def get_location_repository(db: Session = Depends(get_db)):
    return LocationRepository(db)

def get_location_service(
    repo: LocationRepository = Depends(get_location_repository)
):
    return LocationService(repo)