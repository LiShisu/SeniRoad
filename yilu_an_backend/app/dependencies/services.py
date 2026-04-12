from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.repositories.device_repository import DeviceRepository
from app.repositories.navigation_record_repository import NavigationRecordRepository
from app.repositories.voice_log_repository import VoiceLogRepository
from app.services.device import DeviceService
from app.services.navigation_record import NavigationRecordService
from app.services.voice_log import VoiceLogService
from app.services.ai_parser import AIParserService
from app.services.navigation import NavigationService

# Device 相关依赖
def get_device_repository(db: Session = Depends(get_db)):
    """获取设备仓库
    
    创建并返回设备仓库实例
    
    Args:
        db: 数据库会话
    
    Returns:
        DeviceRepository: 设备仓库实例
    """
    return DeviceRepository(db)

def get_device_service(device_repo: DeviceRepository = Depends(get_device_repository)):
    """获取设备服务
    
    创建并返回设备服务实例
    
    Args:
        device_repo: 设备仓库实例
    
    Returns:
        DeviceService: 设备服务实例
    """
    return DeviceService(device_repo)



# NavigationRecord 相关依赖
def get_navigation_record_repository(db: Session = Depends(get_db)):
    """获取导航记录仓库
    
    创建并返回导航记录仓库实例
    
    Args:
        db: 数据库会话
    
    Returns:
        NavigationRecordRepository: 导航记录仓库实例
    """
    return NavigationRecordRepository(db)

def get_navigation_record_service(navigation_record_repo: NavigationRecordRepository = Depends(get_navigation_record_repository)):
    """获取导航记录服务
    
    创建并返回导航记录服务实例
    
    Args:
        navigation_record_repo: 导航记录仓库实例
    
    Returns:
        NavigationRecordService: 导航记录服务实例
    """
    return NavigationRecordService(navigation_record_repo)

# VoiceLog 相关依赖
def get_voice_log_repository(db: Session = Depends(get_db)):
    """获取语音日志仓库
    
    创建并返回语音日志仓库实例
    
    Args:
        db: 数据库会话
    
    Returns:
        VoiceLogRepository: 语音日志仓库实例
    """
    return VoiceLogRepository(db)

def get_voice_log_service(voice_log_repo: VoiceLogRepository = Depends(get_voice_log_repository)):
    """获取语音日志服务
    
    创建并返回语音日志服务实例
    
    Args:
        voice_log_repo: 语音日志仓库实例
    
    Returns:
        VoiceLogService: 语音日志服务实例
    """
    return VoiceLogService(voice_log_repo)

# AIParser 相关依赖
def get_ai_parser_service():
    """获取AI解析服务
    
    创建并返回AI解析服务实例
    
    Returns:
        AIParserService: AI解析服务实例
    """
    return AIParserService()

# Navigation 相关依赖
def get_navigation_service():
    """获取导航服务
    
    创建并返回导航服务实例
    
    Returns:
        NavigationService: 导航服务实例
    """
    return NavigationService()
