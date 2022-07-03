"""本模块包含了 Monitor 的一些工具函数
FrontMatter:
    sidebar_position: 8
    description: wechat_bot.utils 模块
"""
import asyncio
import hashlib
import inspect
import re
from functools import wraps, partial
from typing import Any, Dict, TypeVar, Callable
from typing import (
    Awaitable
)

from loguru import logger
from pydantic.fields import ModelField
from pydantic.typing import ForwardRef, evaluate_forwardref

from .exception import TypeMisMatch

V = TypeVar("V")


def escape_tag(s: str) -> str:
    """用于记录带颜色日志时转义 `<tag>` 类型特殊标签
    参考: [loguru color 标签](https://loguru.readthedocs.io/en/stable/api/logger.html#color)
    参数:
        s: 需要转义的字符串
    """
    return re.sub(r"</?((?:[fb]g\s)?[^<>\s]*)>", r"\\\g<0>", s)


def run_sync(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    """
    :说明:

      一个用于包装 sync function 为 async function 的装饰器

    :参数:

      * ``func: Callable[..., Any]``: 被装饰的同步函数

    :返回:

      - ``Callable[..., Awaitable[Any]]``
    """

    @wraps(func)
    async def _wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        pfunc = partial(func, *args, **kwargs)
        result = await loop.run_in_executor(None, pfunc)
        return result

    return _wrapper


def is_coroutine_callable(call: Callable[..., Any]) -> bool:
    """检查 call 是否是一个 callable 协程函数"""
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    func_ = getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(func_)


def get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    """获取可调用对象签名"""
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def get_typed_annotation(param: inspect.Parameter, globalns: Dict[str, Any]) -> Any:
    """获取参数的类型注解"""
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        try:
            annotation = evaluate_forwardref(annotation, globalns, globalns)
        except Exception as e:
            logger.opt(colors=True, exception=e).warning(
                f'Unknown ForwardRef["{param.annotation}"] for parameter {param.name}'
            )
            return inspect.Parameter.empty
    return annotation


def check_field_type(field: ModelField, value: V) -> V:
    _, errs_ = field.validate(value, {}, loc=())
    if errs_:
        raise TypeMisMatch(field, value)
    return value


def try_except(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info('异常处理')
        message = kwargs.get('message')
        try:
            await func(*args, **kwargs)
        except Exception as e:
            if str(e):
                if message:
                    message.wx.send_text(message.group, f'Error:{e}')

    return wrapper


def MD5(code):
    md5 = hashlib.md5()
    md5.update(code.encode('utf-8'))
    return md5.hexdigest()
