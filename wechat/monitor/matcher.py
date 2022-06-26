import inspect
from collections import defaultdict
from contextvars import ContextVar
from typing import Type, List, Dict, Union, Callable, Optional

from ..monitor.exception import StopPropagation, FinishedException
from ..monitor.logger import logger
from .rule import Rule
from .typing import T_Handler

matchers: Dict[int, List[Type["Matcher"]]] = defaultdict(list)
"""
:类型: ``Dict[int, List[Type[Matcher]]]``
:说明: 用于存储当前所有的事件响应器
"""

current_message: ContextVar = ContextVar("current_message")


class MatcherMeta(type):

    def __repr__(self) -> str:
        return (f"<Matcher from {self.module or 'unknow'}, "  # type: ignore
                f"type={self.type}, priority={self.priority}, "  # type: ignore
                f"temp={self.temp}>")  # type: ignore

    def __str__(self) -> str:
        return repr(self)


class Matcher(metaclass=MatcherMeta):
    """事件响应器类"""
    module: Optional[str] = None
    """
    :类型: ``Optional[str]``
    :说明: 事件响应器所在模块名称
    """

    type: str = ""
    """
    :类型: ``str``
    :说明: 事件响应器类型
    """
    rule: Rule = Rule()
    """
    :类型: ``Rule``
    :说明: 事件响应器匹配规则
    """
    handlers: List[T_Handler] = []
    """
    :类型: ``List[T_Handler]``
    :说明: 事件响应器拥有的事件处理函数列表
    """
    priority: int = 1
    """
    :类型: ``int``
    :说明: 事件响应器优先级
    """
    block: bool = False
    """
    :类型: ``bool``
    :说明: 事件响应器是否阻止事件传播
    """
    temp: bool = False
    """
    :类型: ``bool``
    :说明: 事件响应器是否为临时
    """

    def __init__(self):
        """实例化 Matcher 以便运行"""
        self.handlers = self.handlers.copy()

    def __repr__(self) -> str:
        return (f"<Matcher from {self.module or 'unknown'}, type={self.type}, "
                f"priority={self.priority}, temp={self.temp}>")

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def new(cls,
            type_: str = "",
            rule: Optional[Rule] = None,
            handlers: Optional[List[T_Handler]] = None,
            temp: bool = False,
            priority: int = 1,
            block: bool = False,
            *,
            module: Optional[str] = None) -> Type["Matcher"]:
        """
        :说明:

          创建一个新的事件响应器，并存储至 `matchers <#matchers>`_

        :参数:

          * ``type_: str``: 事件响应器类型，与 ``event.get_type()`` 一致时触发，空字符串表示任意
          * ``handlers: Optional[List[T_Handler]]``: 事件处理函数列表
          * ``temp: bool``: 是否为临时事件响应器，即触发一次后删除
          * ``priority: int``: 响应优先级
          * ``block: bool``: 是否阻止事件向更低优先级的响应器传播
          * ``module: Optional[str]``: 事件响应器所在模块名称

        :返回:

          - ``Type[Matcher]``: 新的事件响应器类
        """

        NewMatcher = type(
            "Matcher", (Matcher,), {
                "module":
                    module,
                "type":
                    type_,
                "rule":
                    rule or Rule(),
                "handlers": [
                    cls.process_handler(handler) for handler in handlers
                ] if handlers else [],
                "temp":
                    temp,
                "priority":
                    priority,
                "block":
                    block,
            })

        matchers[priority].append(NewMatcher)

        return NewMatcher

    @classmethod
    async def check_rule(cls, message: "Message") -> bool:
        """
        :说明:

          检查是否满足匹配规则

        :参数:

          * ``message: Message``: Message 对象

        :返回:

          - ``bool``: 是否满足匹配规则
        """
        return await cls.rule(message)

    @staticmethod
    def process_handler(handler: T_Handler) -> T_Handler:
        signature = inspect.signature(handler, follow_wrapped=False)
        message = signature.parameters.get("message")
        if not message:
            raise ValueError("Handler missing parameter 'message'")
        handler.__params__ = {
            "message": message.annotation,
        }
        return handler

    @classmethod
    def append_handler(cls, handler: T_Handler) -> None:
        # Process handler first
        cls.handlers.append(cls.process_handler(handler))

    @classmethod
    def handle(cls) -> Callable[[T_Handler], T_Handler]:
        """
        :说明:

          装饰一个函数来向事件响应器直接添加一个处理函数

        :参数:

          * 无
        """

        def _decorator(func: T_Handler) -> T_Handler:
            cls.append_handler(func)
            return func

        return _decorator

    @classmethod
    async def send(cls, msg: Union[str],
                   **kwargs):
        """
        :说明:

          发送一条消息给当前交互用户

        :参数:

          * ``msg: Union[str]``: 消息内容
          * ``**kwargs``: 其他传递给 ``message.send`` 的参数
        """
        message = current_message.get()
        await message.send(message=msg, **kwargs)

    def stop_propagation(self):
        """
        :说明:

          阻止事件传播
        """
        self.block = True

    async def run_handler(self, handler: T_Handler, message: "Message"):
        if not hasattr(handler, "__params__"):
            self.process_handler(handler)
        params = getattr(handler, "__params__")

        MessageType = ((params["message"] is not inspect.Parameter.empty) and
                       inspect.isclass(params["message"]) and params["message"])

        if MessageType and not isinstance(message, MessageType):
            logger.debug(
                f"Matcher {self} message type {type(message)} not match annotation {MessageType}, ignored"
            )
            return

        args = {"message": message}
        await handler(
            **{k: v for k, v in args.items() if params[k] is not None})

    # 运行handlers
    async def run(self, message: "Message"):
        m_g = current_message.set(message)
        try:

            for _ in range(len(self.handlers)):
                handler = self.handlers.pop(0)

                await self.run_handler(handler, message)

        except FinishedException:
            pass

        except StopPropagation:

            self.block = True

        finally:
            logger.info(f"Matcher {self} running complete")
            current_message.reset(m_g)
