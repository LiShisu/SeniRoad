from fastapi import FastAPI
from app.api.v1 import router as v1_router
from app.api import websocket
from app.middleware import LoggingMiddleware, setup_cors
from app.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="颐路安后端服务",
    description="老年人智能导航助手API",
    version="3.0.0"
)

# 配置中间件
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# 注册路由
app.include_router(v1_router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}
