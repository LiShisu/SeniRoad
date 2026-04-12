#!/bin/bash

# =============================================================================
# 颐路安后端项目初始化脚本
# 功能：创建完整的FastAPI项目目录结构和基础文件
# 用法：bash init_project.sh
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目名称
PROJECT_NAME="yilu_an_backend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   颐路安后端项目初始化脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 创建项目根目录
echo -e "${YELLOW}[1/10] 创建项目根目录...${NC}"
mkdir -p ${PROJECT_NAME}
cd ${PROJECT_NAME}

# 2. 创建 app 目录结构
echo -e "${YELLOW}[2/10] 创建 app 目录结构...${NC}"
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/api/v1
mkdir -p app/services
mkdir -p app/utils
mkdir -p app/middleware

# 3. 创建其他目录
echo -e "${YELLOW}[3/10] 创建测试和配置目录...${NC}"
mkdir -p tests

# 4. 创建所有 __init__.py 文件
echo -e "${YELLOW}[4/10] 创建 __init__.py 文件...${NC}"
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
touch app/middleware/__init__.py
touch tests/__init__.py

# 5. 创建核心配置文件
echo -e "${YELLOW}[5/10] 创建核心配置文件...${NC}"

# main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, user, navigation, location, destination, binding
from app.api import websocket
from app.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="颐路安后端服务",
    description="老年人智能导航助手API",
    version="3.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(user.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(navigation.router, prefix="/api/v1/navigation", tags=["导航"])
app.include_router(location.router, prefix="/api/v1/location", tags=["位置"])
app.include_router(destination.router, prefix="/api/v1/destinations", tags=["目的地"])
app.include_router(binding.router, prefix="/api/v1/bindings", tags=["绑定"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}
EOF

# config.py
cat > app/config.py << 'EOF'
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/yilu_an"
    REDIS_URL: str = "redis://localhost:6379"
    
    # API密钥
    AMAP_API_KEY: str = ""
    QWEN_API_KEY: str = ""
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = 30
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
EOF

# database.py
cat > app/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

echo -e "${GREEN}   ✓ 核心配置文件创建完成${NC}"

# 6. 创建 Models
echo -e "${YELLOW}[6/10] 创建数据模型...${NC}"

# models/user.py
cat > app/models/user.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime

class UserRole(enum.Enum):
    ELDERLY = "elderly"
    FAMILY = "family"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    nickname = Column(String(50))
    role = Column(Enum(UserRole), nullable=False)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    locations = relationship("Location", back_populates="user")
    destinations = relationship("Destination", back_populates="user")
    bindings_elderly = relationship("Binding", foreign_keys="Binding.elderly_id", back_populates="elderly")
    bindings_family = relationship("Binding", foreign_keys="Binding.family_id", back_populates="family")
EOF

# models/location.py
cat > app/models/location.py << 'EOF'
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255))
    accuracy = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="locations")
EOF

# models/destination.py
cat > app/models/destination.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Destination(Base):
    __tablename__ = "destinations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    is_common = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="destinations")
EOF

# models/binding.py
cat > app/models/binding.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime

class BindingStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Binding(Base):
    __tablename__ = "bindings"
    
    id = Column(Integer, primary_key=True, index=True)
    elderly_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    family_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(BindingStatus), default=BindingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.now)
    approved_at = Column(DateTime)
    
    elderly = relationship("User", foreign_keys=[elderly_id], back_populates="bindings_elderly")
    family = relationship("User", foreign_keys=[family_id], back_populates="bindings_family")
EOF

echo -e "${GREEN}   ✓ 数据模型创建完成${NC}"

# 7. 创建 Schemas
echo -e "${YELLOW}[7/10] 创建 Pydantic 数据验证...${NC}"

# schemas/user.py
cat > app/schemas/user.py << 'EOF'
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ELDERLY = "elderly"
    FAMILY = "family"

class UserBase(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20)
    nickname: Optional[str] = None
    role: UserRole
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
EOF

# schemas/location.py
cat > app/schemas/location.py << 'EOF'
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LocationBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    accuracy: Optional[float] = None

class LocationUpdate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
EOF

# schemas/destination.py
cat > app/schemas/destination.py << 'EOF'
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DestinationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_common: bool = False

class DestinationCreate(DestinationBase):
    pass

class DestinationResponse(DestinationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
EOF

# schemas/binding.py
cat > app/schemas/binding.py << 'EOF'
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class BindingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class BindingCreate(BaseModel):
    elderly_id: int
    family_id: int

class BindingResponse(BaseModel):
    id: int
    elderly_id: int
    family_id: int
    status: BindingStatus
    created_at: datetime
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
EOF

echo -e "${GREEN}   ✓ Pydantic 数据验证创建完成${NC}"

# 8. 创建 API 路由
echo -e "${YELLOW}[8/10] 创建 API 路由...${NC}"

# api/v1/auth.py
cat > app/api/v1/auth.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import AuthService
from app.schemas.user import UserCreate, UserResponse
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    auth_service = AuthService(db)
    return await auth_service.register(user)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    auth_service = AuthService(db)
    return await auth_service.login(form_data.username, form_data.password)
EOF

# api/v1/user.py
cat > app/api/v1/user.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.middleware.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    return current_user

@router.put("/profile")
async def update_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新用户信息"""
    pass
EOF

# api/v1/navigation.py
cat > app/api/v1/navigation.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from app.services.navigation import NavigationService
from app.services.ai_parser import AIParserService
from app.middleware.auth import get_current_user

router = APIRouter()

@router.post("/plan")
async def plan_route(
    request: dict,
    current_user: dict = Depends(get_current_user),
    nav_service: NavigationService = Depends()
):
    """规划导航路线"""
    pass

@router.get("/common-destinations")
async def get_common_destinations(current_user: dict = Depends(get_current_user)):
    """获取常用地点列表"""
    pass
EOF

# api/v1/location.py
cat > app/api/v1/location.py << 'EOF'
from fastapi import APIRouter, Depends
from app.database import get_db
from app.middleware.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/update")
async def update_location(
    location_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新实时位置"""
    pass

@router.get("/history")
async def get_location_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询历史轨迹"""
    pass
EOF

# api/v1/destination.py
cat > app/api/v1/destination.py << 'EOF'
from fastapi import APIRouter, Depends
from app.database import get_db
from app.middleware.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/")
async def list_destinations(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取目的地列表"""
    pass

@router.post("/")
async def create_destination(
    dest_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建目的地"""
    pass
EOF

# api/v1/binding.py
cat > app/api/v1/binding.py << 'EOF'
from fastapi import APIRouter, Depends
from app.database import get_db
from app.middleware.auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/")
async def create_binding(
    binding_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建绑定关系"""
    pass

@router.get("/")
async def list_bindings(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取绑定关系列表"""
    pass
EOF

# api/websocket.py
cat > app/api/websocket.py << 'EOF'
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.location import LocationService
from typing import Dict

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

@router.websocket("/location/{user_id}")
async def websocket_location(websocket: WebSocket, user_id: str):
    """WebSocket实时位置推送"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await LocationService.update_location(user_id, data)
            await LocationService.push_to_family(user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
EOF

echo -e "${GREEN}   ✓ API 路由创建完成${NC}"

# 9. 创建 Services 和 Utils
echo -e "${YELLOW}[9/10] 创建业务逻辑层和工具函数...${NC}"

# services/auth.py
cat > app/services/auth.py << 'EOF'
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    async def register(self, user_data):
        pass
    
    async def login(self, phone: str, password: str):
        pass
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
EOF

# services/navigation.py
cat > app/services/navigation.py << 'EOF'
from httpx import AsyncClient
from app.config import settings

class NavigationService:
    def __init__(self):
        self.client = AsyncClient()
        self.amap_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
    
    async def plan_route(self, origin: str, destination: str, priority: str = "elderly_friendly"):
        params = {
            "origin": origin,
            "destination": destination,
            "key": self.amap_key,
            "extensions": "all"
        }
        response = await self.client.get(f"{self.base_url}/direction/walking", params=params)
        return response.json()
    
    def _filter_elderly_friendly(self, route_data: dict) -> dict:
        return route_data
EOF

# services/location.py
cat > app/services/location.py << 'EOF'
class LocationService:
    @staticmethod
    async def update_location(user_id: str, data: dict):
        pass
    
    @staticmethod
    async def push_to_family(user_id: str, data: dict):
        pass
EOF

# services/ai_parser.py
cat > app/services/ai_parser.py << 'EOF'
from httpx import AsyncClient
from app.config import settings

class AIParserService:
    def __init__(self):
        self.client = AsyncClient()
        self.qwen_api_key = settings.QWEN_API_KEY
    
    async def parse_destination(self, user_input: str) -> dict:
        prompt = f"请解析以下老年人的口语化目的地表达：{user_input}"
        response = await self.client.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers={"Authorization": f"Bearer {self.qwen_api_key}"},
            json={"model": "qwen-max", "input": {"prompt": prompt}}
        )
        return response.json()
EOF

# services/notification.py
cat > app/services/notification.py << 'EOF'
class NotificationService:
    @staticmethod
    async def send_push_notification(user_id: str, message: str):
        pass
    
    @staticmethod
    async def send_sms(phone: str, message: str):
        pass
EOF

# utils/security.py
cat > app/utils/security.py << 'EOF'
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
EOF

# utils/validators.py
cat > app/utils/validators.py << 'EOF'
import re

def validate_phone(phone: str) -> bool:
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_coordinates(lat: float, lng: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lng <= 180
EOF

# middleware/auth.py
cat > app/middleware/auth.py << 'EOF'
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"user_id": user_id}
EOF

echo -e "${GREEN}   ✓ 业务逻辑层和工具函数创建完成${NC}"

# 10. 创建项目配置文件
echo -e "${YELLOW}[10/10] 创建项目配置文件...${NC}"

# requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pymysql==1.1.0
redis==5.0.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.26.0
websockets==12.0
python-multipart==0.0.6
alembic==1.13.1
EOF

# .env
cat > .env << 'EOF'
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/yilu_an
REDIS_URL=redis://localhost:6379
AMAP_API_KEY=your_amap_key
QWEN_API_KEY=your_qwen_key
JWT_SECRET_KEY=your_jwt_secret
EOF

# .env.example
cat > .env.example << 'EOF'
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/yilu_an
REDIS_URL=redis://localhost:6379
AMAP_API_KEY=your_amap_key
QWEN_API_KEY=your_qwen_key
JWT_SECRET_KEY=your_jwt_secret
EOF

# .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/
*.db
*.log
.DS_Store
EOF

# README.md
cat > README.md << 'EOF'
# 颐路安后端服务

老年人智能导航助手 FastAPI 后端

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000