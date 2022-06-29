import inspect
from collections import defaultdict
from contextvars import ContextVar
from functools import wraps
from typing import Type, List, Dict, Union, Callable, Optional, TYPE_CHECKING, NoReturn

from monitor.exception import StopPropagation, FinishedException, PausedException, RejectedException
from monitor.logger import logger
from classes import Message
from .rule import Rule
from .typing import T_Handler, T_State, T_StateFactory, T_ArgsParser, T_TypeUpdater

if TYPE_CHECKING:
    from classes import Message

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

    _default_state: T_State = {}
    """
    :类型: ``T_State``
    :说明: 事件响应器默认状态
    """
    _default_state_factory: Optional[T_StateFactory] = None
    """
    :类型: ``Optional[T_State]``
    :说明: 事件响应器默认工厂函数
    """

    _default_parser: Optional[T_ArgsParser] = None
    """
    :类型: ``Optional[T_ArgsParser]``
    :说明: 事件响应器默认参数解析函数
    """
    _default_type_updater: Optional[T_TypeUpdater] = None
    """
    :类型: ``Optional[T_ArgsParser]``
    :说明: 事件响应器类型更新函数
    """

    def __init__(self):
        """实例化 Matcher 以便运行"""
        self.handlers = self.handlers.copy()
        self.state = self._default_state.copy()

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
            module: Optional[str] = None,
            default_state: Optional[T_State] = None,
            default_state_factory: Optional[T_StateFactory] = None,
            ) -> Type["Matcher"]:
        """
        :说明:

          创建一个新的事件响应器，并存储至 `matchers <#matchers>`_

        :参数:

          * ``type_: str``: 事件响应器类型，与 ``event.get_type()`` 一致时触发，空字符串表示任意
          * ``rule: Optional[Rule]``: 匹配规则
          * ``handlers: Optional[List[T_Handler]]``: 事件处理函数列表
          * ``temp: bool``: 是否为临时事件响应器，即触发一次后删除
          * ``priority: int``: 响应优先级
          * ``block: bool``: 是否阻止事件向更低优先级的响应器传播
          * ``module: Optional[str]``: 事件响应器所在模块名称
          * ``default_state: Optional[T_State]``: 默认状态 ``state``
          * ``default_state_factory: Optional[T_StateFactory]``: 默认状态 ``state`` 的工厂函数

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
                "_default_state":
                    default_state or {},
                "_default_state_factory":
                    staticmethod(default_state_factory)
                    if default_state_factory else None
            })

        matchers[priority].append(NewMatcher)

        return NewMatcher

    @classmethod
    async def check_rule(cls, message: "Message", state: T_State) -> bool:
        """
        :说明:

          检查是否满足匹配规则

        :参数:

          * ``message: Message``: Message 对象

        :返回:

          - ``bool``: 是否满足匹配规则
        """
        return await cls.rule(message, state)

    @classmethod
    def args_parser(cls, func: T_ArgsParser) -> T_ArgsParser:
        """
        :说明:

          装饰一个函数来更改当前事件响应器的默认参数解析函数

        :参数:

          * ``func: T_ArgsParser``: 参数解析函数
        """
        cls._default_parser = func
        return func

    @classmethod
    def type_updater(cls, func: T_TypeUpdater) -> T_TypeUpdater:
        """
        :说明:

          装饰一个函数来更改当前事件响应器的默认响应事件类型更新函数

        :参数:

          * ``func: T_TypeUpdater``: 响应事件类型更新函数
        """
        cls._default_type_updater = func
        return func

    @staticmethod
    def process_handler(handler: T_Handler) -> T_Handler:
        signature = inspect.signature(handler, follow_wrapped=False)
        message = signature.parameters.get("message")
        state = signature.parameters.get("state")
        matcher = signature.parameters.get("matcher")

        if not message:
            raise ValueError("Handler missing parameter 'message'")
        handler.__params__ = {
            "message": message.annotation,
            "state": T_State if state else None,
            "matcher": matcher.annotation if matcher else None
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
    def receive(cls) -> Callable[[T_Handler], T_Handler]:
        """
        :说明:

          装饰一个函数来指示 Monitor 在接收用户新的一条消息后继续运行该函数

        :参数:

          * 无
        """

        async def _receive(message: "Message") -> NoReturn:
            raise PausedException

        cls.process_handler(_receive)

        if cls.handlers:
            # 已有前置handlers则接受一条新的消息，否则视为接收初始消息
            cls.append_handler(_receive)

        def _decorator(func: T_Handler) -> T_Handler:
            cls.process_handler(func)
            if not cls.handlers or cls.handlers[-1] is not func:
                cls.append_handler(func)

            _receive.__params__.update({
                "message":
                    func.__params__["message"],
            })

            return func

        return _decorator

    @classmethod
    def got(
            cls,
            key: str,
            prompt: Optional[Union[str, "Message"]] = None,
            args_parser: Optional[T_ArgsParser] = None
    ) -> Callable[[T_Handler], T_Handler]:
        """
        :说明:

          装饰一个函数来指示 Monitor 当要获取的 ``key`` 不存在时接收用户新的一条消息并经过 ``ArgsParser`` 处理后再运行该函数，如果 ``key`` 已存在则直接继续运行

        :参数:

          * ``key: str``: 参数名
          * ``prompt: Optional[Union[str, Message]]``: 在参数不存在时向用户发送的消息
          * ``args_parser: Optional[T_ArgsParser]``: 可选参数解析函数，空则使用默认解析函数
        """

        async def _key_getter(message: "Message", state: T_State):
            state["_current_key"] = key
            if key not in state:
                if prompt:
                    if isinstance(prompt, str):
                        friend = message.group or message.user
                        await message.wx.send_text(friend, prompt.format(**state))
                    elif isinstance(prompt, Message):
                        friend = prompt.group or prompt.user
                        await message.wx.send_text(friend, prompt.msg.format(**state))
                    else:
                        logger.warning("Unknown prompt type, ignored.")
                raise PausedException
            else:
                state["_skip_key"] = True

        async def _key_parser(message: "Message", state: T_State):
            if key in state and state.get("_skip_key"):
                del state["_skip_key"]
                return
            parser = args_parser or cls._default_parser
            if parser:
                # parser = cast(T_ArgsParser["Bot", "Event"], parser)
                await parser(message, state)
            else:
                state[state["_current_key"]] = str(message.get_message())

        cls.append_handler(_key_getter)
        cls.append_handler(_key_parser)

        def _decorator(func: T_Handler) -> T_Handler:
            if not hasattr(cls.handlers[-1], "__wrapped__"):
                cls.process_handler(func)
                parser = cls.handlers.pop()

                @wraps(func)
                async def wrapper(message: "Message", state: T_State,
                                  matcher: Matcher):
                    await matcher.run_handler(parser, message, state)
                    await matcher.run_handler(func, message, state)
                    if "_current_key" in state:
                        del state["_current_key"]

                cls.append_handler(wrapper)

                wrapper.__params__.update({
                    "message":
                        func.__params__["message"],
                })
                _key_getter.__params__.update({
                    "message":
                        func.__params__["message"],
                })
                _key_parser.__params__.update({
                    "message":
                        func.__params__["message"],
                })

            return func

        return _decorator

    @classmethod
    async def send(cls, msg: Union[str, "Message"],
                   **kwargs):
        """
        :说明:

          发送一条消息给当前交互用户

        :参数:

          * ``msg: Union[str]``: 消息内容
          * ``**kwargs``: 其他传递给 ``message.wx.send_text`` 的参数
        """
        message = current_message.get()
        if isinstance(msg, Message):
            _message = msg.get_message()
            friend = msg.group or msg.user
        elif isinstance(msg, str):
            _message = msg
            friend = message.group or message.user
        else:
            _message, friend = None, None
        if _message and friend:
            await message.wx.send_text(friend, _message, **kwargs)
        else:
            raise FinishedException

    @classmethod
    async def finish(cls,
                     msg: Optional[Union[str, "Message"]] = None,
                     **kwargs) -> NoReturn:
        """
        :说明:

          发送一条消息给当前交互用户并结束当前事件响应器

        :参数:

          * ``message: Union[str, Message]``: 消息内容
          * ``**kwargs``: 其他传递给 ``message.wx.send_text`` 的参数，请参考对应 adapter 的 bot 对象 api
        """
        await cls.send(msg, **kwargs)

        raise FinishedException

    @classmethod
    async def pause(cls,
                    prompt: Optional[Union[str, "Message"]] = None,
                    **kwargs) -> NoReturn:
        """
        :说明:

          发送一条消息给当前交互用户并暂停事件响应器，在接收用户新的一条消息后继续下一个处理函数

        :参数:

          * ``prompt: Union[str, Message]``: 消息内容
          * ``**kwargs``: 其他传递给 ``message.wx.send_text`` 的参数，请参考对应 adapter 的 bot 对象 api
        """
        await cls.send(prompt, **kwargs)

        raise PausedException

    @classmethod
    async def reject(cls,
                     prompt: Optional[Union[str, "Message"]] = None,
                     **kwargs) -> NoReturn:
        """
        :说明:

          发送一条消息给当前交互用户并暂停事件响应器，在接收用户新的一条消息后重新运行当前处理函数

        :参数:

          * ``prompt: Union[str, Message]``: 消息内容
          * ``**kwargs``: 其他传递给 ``message.wx.send_text`` 的参数，请参考对应 adapter 的 bot 对象 api
        """
        await cls.send(prompt, **kwargs)

        raise RejectedException

    def stop_propagation(self):
        """
        :说明:

          阻止事件传播
        """
        self.block = True

    async def run_handler(self, handler: T_Handler, message: "Message", state: T_State):
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

        args = {"message": message, "state": state, "matcher": self}
        await handler(
            **{k: v for k, v in args.items() if params[k] is not None})

    # 运行handlers
    async def run(self, message: "Message", state: T_State):
        m_g = current_message.set(message)
        try:
            # Refresh preprocess state
            state_ = await self._default_state_factory(message) \
                if self._default_state_factory else self.state
            state_.update(state)

            for _ in range(len(self.handlers)):
                handler = self.handlers.pop(0)
                await self.run_handler(handler, message, state_)

        except RejectedException:
            self.handlers.insert(0, handler)  # type: ignore
            if self._default_type_updater:
                type_ = await self._default_type_updater(
                    message, state, self.type)
            else:
                type_ = "message"
            Matcher.new(type_,
                        Rule(),
                        self.handlers,
                        temp=True,
                        priority=0,
                        block=True,
                        module=self.module,
                        default_state=self.state)
        except PausedException:
            if self._default_type_updater:
                type_ = await self._default_type_updater(
                    message, state, self.type)
            else:
                type_ = "message"
            Matcher.new(type_,
                        Rule(),
                        self.handlers,
                        temp=True,
                        priority=0,
                        block=True,
                        module=self.module,
                        default_state=self.state)
        except FinishedException:
            pass

        except StopPropagation:
            self.block = True

        finally:
            logger.info(f"Matcher {self} running complete")
            current_message.reset(m_g)
