from datetime import datetime, timedelta
from app.config import settings, pwd_context
from jose import jwt

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌
    
    生成 JWT 访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间
    
    Returns:
        str: 编码后的 JWT 令牌
    """
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def hash_password(password: str) -> str:
    """哈希密码
    
    使用 bcrypt 算法对密码进行哈希处理
    
    Args:
        password: 原始密码
    
    Returns:
        str: 哈希后的密码
    """
    # bcrypt 只处理前72个字节的密码
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    
    验证原始密码是否与哈希密码匹配
    
    Args:
        plain_password: 原始密码
        hashed_password: 哈希后的密码
    
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)
