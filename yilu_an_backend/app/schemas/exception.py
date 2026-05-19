from fastapi import status

class BusinessException(Exception):
    """业务逻辑异常基类"""
    def __init__(self, message: str, code: int = 400, http_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.code = code
        self.http_code = http_code

class NotFoundException(BusinessException):
    """资源不存在异常 (404)"""
    def __init__(self, message: str = "请求的资源不存在"):
        super().__init__(message=message, code=404, http_code=status.HTTP_404_NOT_FOUND)

class ForbiddenException(BusinessException):
    """权限不足异常 (403)"""
    def __init__(self, message: str = "没有操作权限"):
        super().__init__(message=message, code=403, http_code=status.HTTP_403_FORBIDDEN)

class UnauthorizedException(BusinessException):
    """未授权异常 (401)"""
    def __init__(self, message: str = "登录已过期，请重新登录"):
        super().__init__(message=message, code=401, http_code=status.HTTP_401_UNAUTHORIZED)

class AmapApiException(BusinessException):
    """高德地图API调用异常"""
    def __init__(self, message: str):
        super().__init__(message=message, code=500, http_code=status.HTTP_500_INTERNAL_SERVER_ERROR)