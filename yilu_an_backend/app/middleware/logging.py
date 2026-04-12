import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件
    
    记录所有请求和响应的详细信息，包括：
    - 请求方法和路径
    - 响应状态码
    - 请求处理时间
    - 客户端IP地址
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求并记录日志
        
        Args:
            request: HTTP 请求对象
            call_next: 下一个中间件或路由处理器
        
        Returns:
            Response: HTTP 响应对象
        """
        start_time = time.time()
        
        # 记录请求信息
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {client_host} - "
            f"Query: {request.url.query}"
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应信息
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Path: {request.url.path}"
        )
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
