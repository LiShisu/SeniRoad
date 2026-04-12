#!/usr/bin/env python3
"""测试模块导入是否正常"""

import sys

def test_imports():
    """测试各个模块的导入"""
    print("测试模块导入...")
    
    # 测试基础模块
    try:
        import app
        print("✓ app 模块导入成功")
    except Exception as e:
        print(f"✗ app 模块导入失败: {e}")
    
    # 测试配置模块
    try:
        from app.config import settings
        print("✓ app.config 模块导入成功")
    except Exception as e:
        print(f"✗ app.config 模块导入失败: {e}")
    
    # 测试数据库模块
    try:
        from app.database import get_db
        print("✓ app.database 模块导入成功")
    except Exception as e:
        print(f"✗ app.database 模块导入失败: {e}")
    
    # 测试模型模块
    try:
        from app.models import User
        print("✓ app.models 模块导入成功")
    except Exception as e:
        print(f"✗ app.models 模块导入失败: {e}")
    
    # 测试schemas模块
    try:
        from app.schemas import UserCreate
        print("✓ app.schemas 模块导入成功")
    except Exception as e:
        print(f"✗ app.schemas 模块导入失败: {e}")
    
    # 测试utils模块
    try:
        from app.utils import hash_password, verify_password
        print("✓ app.utils 模块导入成功")
    except Exception as e:
        print(f"✗ app.utils 模块导入失败: {e}")
    
    # 测试repositories模块
    try:
        from app.repositories import UserRepository
        print("✓ app.repositories 模块导入成功")
    except Exception as e:
        print(f"✗ app.repositories 模块导入失败: {e}")
    
    # 测试services模块
    try:
        from app.services.auth import AuthService
        print("✓ app.services.auth 模块导入成功")
    except Exception as e:
        print(f"✗ app.services.auth 模块导入失败: {e}")
    
    # 测试dependencies模块
    try:
        from app.dependencies import get_auth_service
        print("✓ app.dependencies 模块导入成功")
    except Exception as e:
        print(f"✗ app.dependencies 模块导入失败: {e}")
    
    # 测试api模块
    try:
        from app.api.v1 import router as v1_router
        print("✓ app.api.v1 模块导入成功")
    except Exception as e:
        print(f"✗ app.api.v1 模块导入失败: {e}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_imports()
