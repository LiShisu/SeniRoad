from pydantic import BaseModel

class BaseSchema(BaseModel):
    pass

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class Result(GenericModel, Generic[T]):
    """统一响应结构"""
    code: int  # 业务状态码：200-成功，401-未授权，500-系统错误等
    message: str   # 提示信息
    data: Optional[T] = None # 具体数据内容