import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件
    
    记录所有请求和响应的详细信息，包括：
    - 请求方法和路径
    - 请求体（仅 POST/PUT/PATCH）
    - 响应状态码
    - 响应体
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
        
        # 获取客户端IP
        client_host = request.client.host if request.client else "unknown"

        # 初始化请求体变量
        body = None
        body_bytes = None

        # 只解析 POST/PUT/PATCH 请求的请求体
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        body = json.loads(body_bytes.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        body = body_bytes.decode('utf-8', errors='replace')
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")

        # 记录请求信息
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {client_host} - "
            f"Query: {request.url.query} - "
            f"Body: {body}"
        )

        # 如果读取了请求体，需要重新设置 receive 方法供后续处理器使用
        if body_bytes:
            async def receive():
                return {"type": "http.request", "body": body_bytes}
            request._receive = receive

        # 调用下一个中间件或路由处理器
        response = await call_next(request)

        # 记录响应信息（包含响应体）
        process_time = time.time() - start_time
        response_body = await self._get_response_body(response)
        
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Path: {request.url.path} - "
            f"Response Body: {response_body}"
        )

        # 添加处理时间响应头
        response.headers["X-Process-Time"] = str(process_time)

        return response

    async def _get_response_body(self, response: Response) -> str:
        """安全地提取响应体内容
        
        兼容普通 Response 和 StreamingResponse，避免 AttributeError
        
        Args:
            response: HTTP 响应对象
        
        Returns:
            str: 响应体内容（JSON 格式化或原始字符串）
        """
        body_bytes = b""
        
        # 尝试从响应中提取body
        # 使用 hasattr 避免 AttributeError
        if hasattr(response, 'body') and response.body is not None:
            body_bytes = response.body
        elif hasattr(response, 'body_iterator'):
            # 处理流式响应（StreamingResponse）
            body_chunks = []
            try:
                async for chunk in response.body_iterator:
                    body_chunks.append(chunk)
                body_bytes = b''.join(body_chunks)
                # 重新设置异步迭代器以便后续中间件使用
                # 使用异步生成器而不是普通生成器
                async def new_body_iterator():
                    for chunk in body_chunks:
                        yield chunk
                response.body_iterator = new_body_iterator()
            except Exception as e:
                logger.warning(f"Failed to read streaming response body: {e}")
                return "[Streaming response body not readable]"
        else:
            return "[Response body not accessible]"

        # 尝试解析为 JSON，确保中文正常显示
        if body_bytes:
            try:
                return json.dumps(json.loads(body_bytes.decode('utf-8')), ensure_ascii=False)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return body_bytes.decode('utf-8', errors='replace')
        
        return ""
