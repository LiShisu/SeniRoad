# # api/v1/views.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.repositories import (
#     elderly_family_binding,
#     elderly_location,
#     elderly_favorite_places,
#     navigation_stats,
#     voice_interaction_logs
# )

# router = APIRouter(prefix="/views", tags=["views"])

# # 老人家属绑定关系视图
# @router.get("/elderly-family-binding")
# def get_elderly_family_binding(
#     status: str = None,
#     elderly_id: int = None,
#     family_id: int = None,
#     db: Session = Depends(get_db)
# ):
#     """获取老人家属绑定关系"""
#     if status:
#         return elderly_family_binding.ElderlyFamilyBindingViewHandler.get_bindings_by_status(db, status)
#     elif elderly_id:
#         return elderly_family_binding.ElderlyFamilyBindingViewHandler.get_bindings_by_elderly(db, elderly_id)
#     elif family_id:
#         return elderly_family_binding.ElderlyFamilyBindingViewHandler.get_bindings_by_family(db, family_id)
#     else:
#         return elderly_family_binding.ElderlyFamilyBindingViewHandler.get_all_bindings(db)

# # 老人位置信息视图
# @router.get("/elderly-location")
# def get_elderly_location(
#     elderly_id: int = None,
#     db: Session = Depends(get_db)
# ):
#     """获取老人位置信息"""
#     if elderly_id:
#         return elderly_location.ElderlyLocationViewHandler.get_elderly_location(db, elderly_id)
#     else:
#         return elderly_location.ElderlyLocationViewHandler.get_all_elderly_locations(db)

# # 老人常用地点视图
# @router.get("/elderly-favorite-places")
# def get_elderly_favorite_places(
#     elderly_id: int = None,
#     source_type: str = None,
#     db: Session = Depends(get_db)
# ):
#     """获取老人常用地点"""
#     if elderly_id:
#         return elderly_favorite_places.ElderlyFavoritePlacesViewHandler.get_favorite_places_by_elderly(db, elderly_id)
#     elif source_type:
#         return elderly_favorite_places.ElderlyFavoritePlacesViewHandler.get_favorite_places_by_source(db, source_type)
#     else:
#         return elderly_favorite_places.ElderlyFavoritePlacesViewHandler.get_all_favorite_places(db)

# # 导航记录统计视图
# @router.get("/navigation-stats")
# def get_navigation_stats(
#     elderly_id: int = None,
#     year: int = None,
#     month: int = None,
#     dest_name: str = None,
#     db: Session = Depends(get_db)
# ):
#     """获取导航记录统计"""
#     if elderly_id:
#         return navigation_stats.NavigationStatsViewHandler.get_stats_by_elderly(db, elderly_id)
#     elif year and month:
#         return navigation_stats.NavigationStatsViewHandler.get_stats_by_month(db, year, month)
#     elif dest_name:
#         return navigation_stats.NavigationStatsViewHandler.get_stats_by_destination(db, dest_name)
#     else:
#         return navigation_stats.NavigationStatsViewHandler.get_all_stats(db)

# # 语音交互日志视图
# @router.get("/voice-interaction-logs")
# def get_voice_interaction_logs(
#     user_id: int = None,
#     role: str = None,
#     start_time: str = None,
#     end_time: str = None,
#     db: Session = Depends(get_db)
# ):
#     """获取语音交互日志"""
#     if user_id:
#         return voice_interaction_logs.VoiceInteractionLogsViewHandler.get_logs_by_user(db, user_id)
#     elif role:
#         return voice_interaction_logs.VoiceInteractionLogsViewHandler.get_logs_by_role(db, role)
#     elif start_time and end_time:
#         return voice_interaction_logs.VoiceInteractionLogsViewHandler.get_logs_by_time(db, start_time, end_time)
#     else:
#         return voice_interaction_logs.VoiceInteractionLogsViewHandler.get_all_logs(db)
