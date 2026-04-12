from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

def setup_cors(app: FastAPI):
    """配置CORS中间件
    
    配置跨域资源共享，允许前端应用访问API
    
    Args:
        app: FastAPI 应用实例
    """
    app.add_middleware(
        CORSMiddleware,
        # 允许的源地址，生产环境应该指定具体域名
        allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["*"],
        # 允许携带凭证（如cookies）
        allow_credentials=True,
        # 允许的HTTP方法
        allow_methods=["*"],
        # 允许的HTTP头
        allow_headers=["*"],
    )
