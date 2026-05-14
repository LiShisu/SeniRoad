from fastapi import FastAPI,Request,status
from app.api.v1 import router as v1_router
from fastapi.exceptions import RequestValidationError 
#从自定义的文件中只引入 BusinessException
from app.schemas.exception import BusinessException
from app.api import websocket
from app.middleware import LoggingMiddleware, setup_cors
from app.database import engine, Base
from fastapi.responses import JSONResponse
# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="颐路安后端服务",
    description="老年人智能导航助手API",
    version="3.0.0"
)
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """
    捕捉所有手动抛出的 BusinessException
    并转化为统一的 Result 格式
    """
    return JSONResponse(
        status_code=exc.http_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    捕捉参数校验错误 (FastAPI 自动触发)
    将其也转化为统一的 Result 格式，避免返回原生乱码
    """
    # 提取第一个错误信息进行展示
    err_msg = exc.errors()[0].get("message") if exc.errors() else "参数格式不正确"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": f"请求参数错误: {err_msg}",
            "data": None
        }
    )
# 配置中间件
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# 注册路由
app.include_router(v1_router, prefix="/api")
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}