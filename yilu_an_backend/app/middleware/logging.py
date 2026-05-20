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
                f"Body: {req_body_str}"
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
                f"Body: {res_body_str}"
            )