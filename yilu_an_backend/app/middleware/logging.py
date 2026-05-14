# import time
# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.responses import Response
# import logging
# import json

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger("api")

# class LoggingMiddleware(BaseHTTPMiddleware):
#     """日志记录中间件
    
#     记录所有请求和响应的详细信息，包括：
#     - 请求方法和路径
#     - 请求体（仅 POST/PUT/PATCH）
#     - 响应状态码
#     - 响应体
#     - 请求处理时间
#     - 客户端IP地址
#     """
    
#     async def dispatch(self, request: Request, call_next) -> Response:
#         """处理请求并记录日志
        
#         Args:
#             request: HTTP 请求对象
#             call_next: 下一个中间件或路由处理器
        
#         Returns:
#             Response: HTTP 响应对象
#         """
#         start_time = time.time()
        
#         # 获取客户端IP
#         client_host = request.client.host if request.client else "unknown"

#         # 初始化请求体变量
#         body = None
#         body_bytes = None

#         # 只解析 POST/PUT/PATCH 请求的请求体
#         if request.method in ["POST", "PUT", "PATCH"]:
#             try:
#                 body_bytes = await request.body()
#                 if body_bytes:
#                     try:
#                         body = json.loads(body_bytes.decode('utf-8'))
#                     except (json.JSONDecodeError, UnicodeDecodeError):
#                         body = body_bytes.decode('utf-8', errors='replace')
#             except Exception as e:
#                 logger.warning(f"Failed to read request body: {e}")

#         # 记录请求信息
#         logger.info(
#             f"Request: {request.method} {request.url.path} - "
#             f"Client: {client_host} - "
#             f"Query: {request.url.query} - "
#             f"Body: {body}"
#         )

#         # 如果读取了请求体，需要重新设置 receive 方法供后续处理器使用
#         if body_bytes:
#             async def receive():
#                 return {"type": "http.request", "body": body_bytes}
#             request._receive = receive

#         # 调用下一个中间件或路由处理器
#         response = await call_next(request)

#         # 记录响应信息（包含响应体）
#         process_time = time.time() - start_time
#         response_body = await self._get_response_body(response)
        
#         logger.info(
#             f"Response: {response.status_code} - "
#             f"Time: {process_time:.3f}s - "
#             f"Path: {request.url.path} - "
#             f"Response Body: {response_body}"
#         )

#         # 添加处理时间响应头
#         response.headers["X-Process-Time"] = str(process_time)

#         return response

#     async def _get_response_body(self, response: Response) -> str:
#         """安全地提取响应体内容
        
#         兼容普通 Response 和 StreamingResponse，避免 AttributeError
        
#         Args:
#             response: HTTP 响应对象
        
#         Returns:
#             str: 响应体内容（JSON 格式化或原始字符串）
#         """
#         body_bytes = b""
        
#         # 尝试从响应中提取body
#         # 使用 hasattr 避免 AttributeError
#         if hasattr(response, 'body') and response.body is not None:
#             body_bytes = response.body
#         elif hasattr(response, 'body_iterator'):
#             # 处理流式响应（StreamingResponse）
#             body_chunks = []
#             try:
#                 async for chunk in response.body_iterator:
#                     body_chunks.append(chunk)
#                 body_bytes = b''.join(body_chunks)
#                 # 重新设置异步迭代器以便后续中间件使用
#                 # 使用异步生成器而不是普通生成器
#                 async def new_body_iterator():
#                     for chunk in body_chunks:
#                         yield chunk
#                 response.body_iterator = new_body_iterator()
#             except Exception as e:
#                 logger.warning(f"Failed to read streaming response body: {e}")
#                 return "[Streaming response body not readable]"
#         else:
#             return "[Response body not accessible]"

#         # 尝试解析为 JSON，确保中文正常显示
#         if body_bytes:
#             try:
#                 return json.dumps(json.loads(body_bytes.decode('utf-8')), ensure_ascii=False)
#             except (json.JSONDecodeError, UnicodeDecodeError):
#                 return body_bytes.decode('utf-8', errors='replace')
        
#         return ""
import time
import json
import logging
from starlette.types import ASGIApp, Receive, Scope, Send, Message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

class LoggingMiddleware:
    """纯 ASGI 日志记录中间件
    
    采用无阻塞设计，完美兼容 StreamingResponse 流式传输。
    记录所有的请求、响应、IP、耗时，并规避 BaseHTTPMiddleware 的底层异常。
    """
    
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 只处理 HTTP 请求，放行 WebSocket 和 Lifespan 等其他协议
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope.get("method", "")
        path = scope.get("path", "")
        query_string = scope.get("query_string", b"").decode("utf-8", errors="ignore")
        client = scope.get("client")
        client_host = client[0] if client else "unknown"

        # 1. 旁路监听：获取请求体 (Request Body)
        req_body_bytes = b""
        more_body = True

        async def wrapped_receive() -> Message:
            nonlocal req_body_bytes, more_body
            message = await receive()
            if message["type"] == "http.request" and more_body:
                chunk = message.get("body", b"")
                # 限制最大读取 100KB，防止文件上传时把内存撑爆
                if len(req_body_bytes) < 1024 * 100:  
                    req_body_bytes += chunk
                more_body = message.get("more_body", False)
            return message

        # 2. 旁路监听：获取响应体 (Response Body)
        res_body_bytes = b""
        status_code = 500

        async def wrapped_send(message: Message) -> None:
            nonlocal res_body_bytes, status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
                # 注入处理时间 Header (X-Process-Time)
                headers = message.setdefault("headers", [])
                headers.append((b"x-process-time", str(time.time() - start_time).encode("utf-8")))
                
            elif message["type"] == "http.response.body":
                chunk = message.get("body", b"")
                # 限制日志只记录前 100KB 的响应，不阻塞流式传输
                if len(res_body_bytes) < 1024 * 100: 
                    res_body_bytes += chunk
                    
            # 数据看过一眼后，立刻放行发给客户端，绝不阻拦！
            await send(message)

        try:
            # 执行核心应用逻辑
            await self.app(scope, wrapped_receive, wrapped_send)
        finally:
            process_time = time.time() - start_time

            # ==== 格式化并打印 Request 日志 ====
            req_body_str = req_body_bytes.decode("utf-8", errors="replace")
            if req_body_str:
                try:
                    req_body_str = json.dumps(json.loads(req_body_str), ensure_ascii=False)
                except Exception:
                    pass # 非 JSON 格式则保持原样

            logger.info(
                f"Request: {method} {path} - "
                f"Client: {client_host} - "
                f"Query: {query_string} - "
                f"Body: {req_body_str[:1000]}" # 限制打印长度
            )

            # ==== 格式化并打印 Response 日志 ====
            res_body_str = res_body_bytes.decode("utf-8", errors="replace")
            if res_body_str:
                try:
                    # 如果是 SSE 流式数据 (以 event: 开头)，不需要强转 JSON
                    if not res_body_str.startswith("event:"):
                        res_body_str = json.dumps(json.loads(res_body_str), ensure_ascii=False)
                except Exception:
                    pass

            logger.info(
                f"Response: {status_code} - "
                f"Time: {process_time:.3f}s - "
                f"Path: {path} - "
                f"Body: {res_body_str[:1000]}" 
            )