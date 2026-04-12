# 中间件目录
# 包含应用中使用的中间件
"""
中间件在 FastAPI 中是一种特殊的组件，用于在请求到达路由处理器之前或响应返回给客户端之后执行代码

中间件适用场景
- 全局功能（CORS、日志、安全头）
- 需要修改请求或响应
- 性能监控和统计
- 错误处理和异常捕获

请求 → 中间件3 → 中间件2 → 中间件1 → 路由处理器
响应 ← 中间件3 ← 中间件2 ← 中间件1 ← 路由处理器

中间件可以：
1. 全局请求处理 ：拦截所有进入应用的 HTTP 请求
2. 响应处理 ：在响应发送给客户端之前进行处理
3. 跨域处理 ：处理 CORS（跨域资源共享）
4. 日志记录 ：记录请求和响应信息
5. 安全控制 ：添加安全相关的 HTTP 头
6. 性能监控 ：监控请求处理时间
7. 错误处理 ：统一处理异常和错误
"""

from app.middleware.logging import LoggingMiddleware
from app.middleware.cors import setup_cors

__all__ = [
    "LoggingMiddleware",
    "setup_cors"
]
