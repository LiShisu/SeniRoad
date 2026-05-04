from pydantic_settings import BaseSettings
from functools import lru_cache  # 缓存函数调用结果
from passlib.context import CryptContext

class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/yilu_an"
    REDIS_URL: str = "redis://localhost:6379"
    
    # API密钥
    AMAP_API_KEY: str = ""
    TENCENT_MAP_API_KEY: str = ""
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # OAuth2配置
    OAUTH2_TOKEN_URL: str = "/api/v1/auth/wechat/login"
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]  # 生产环境应该指定具体域名
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    TEMP_DIR: str = "temp"
    
    # LLM 配置
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api-inference.modelscope.cn/v1"
    VOICE_MODEL: str = "paraformer-realtime-v2"
    TEXT_MODEL: str = "deepseek-ai/DeepSeek-V3.2"
    
    # DashScope 配置（用于 TTS）
    DASHSCOPE_API_KEY: str = ""
    
    # 微信小程序配置
    WECHAT_APPID: str = ""
    WECHAT_APPSECRET: str = ""
    WECHAT_API_URL: str = "https://api.weixin.qq.com/sns/jscode2session"
    
    model_config = {
        "env_file": ".env",
        # - 通过 env_file = ".env" 从 .env 文件加载环境变量
        # - 环境变量会覆盖默认值，实现不同环境的配置切换
    }

@lru_cache()  # 缓存配置实例，避免重复创建
def get_settings() -> Settings:  # 获取配置实例
    # - 从缓存中获取配置实例，避免重复创建
    # - 如果缓存中不存在实例，会创建一个新的实例并缓存起来
    # - 之后每次调用 get_settings() 都会返回缓存中的实例
    # - 这样可以确保在多线程环境下，每个线程使用的是同一个配置实例
    # - 这样可以避免重复创建配置实例，提高性能
    # - 在 FastAPI 路由中通过 Depends(get_settings) 获取配置实例
    return Settings()

settings = get_settings()

# 密码哈希上下文
# - 使用 bcrypt 算法进行密码哈希
# - auto 模式自动处理过时的哈希方案
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
