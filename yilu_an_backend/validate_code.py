import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

try:
    # 导入所有模型
    from app.models import User, Binding, Location, Device, FavoritePlace, NavigationRecord, VoiceLog
    print("✅ 所有模型导入成功")
    
    # 导入所有验证模式
    from app.schemas import (
        UserResponse, UserUpdate,
        LocationCreate, LocationResponse, LocationUpdate,
        BindingCreate, BindingResponse, BindingUnbind,
        DeviceCreate, DeviceUpdate, DeviceResponse,
        FavoritePlaceCreate, FavoritePlaceUpdate, FavoritePlaceResponse,
        NavigationRecordCreate, NavigationRecordUpdate, NavigationRecordResponse,
        VoiceLogCreate, VoiceLogUpdate, VoiceLogResponse
    )
    print("✅ 所有验证模式导入成功")
    
    # 导入所有仓库
    from app.repositories import (
        UserRepository, BindingRepository, LocationRepository, DeviceRepository,
        NavigationRecordRepository, VoiceLogRepository
    )
    print("✅ 所有仓库导入成功")
    
    # 导入所有服务
    from app.services import (
        UserService, DeviceService, NavigationRecordService, VoiceLogService,
        AIParserService, NavigationService
    )
    print("✅ 所有服务导入成功")
    
    # 导入所有API路由
    from app.api.v1 import (
        auth, user, binding, location, navigation, device,
        navigation_record, voice_log, navigation_agent, views
    )
    print("✅ 所有API路由导入成功")
    
    # 导入所有依赖
    from app.dependencies import services
    print("✅ 所有依赖导入成功")
    
    print("\n🎉 所有模块导入成功，代码验证通过！")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
