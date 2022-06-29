from typing import Any, Union, Callable, NoReturn, Awaitable, Optional, Dict

T_State = Dict[Any, Any]
"""
:类型: ``Dict[Any, Any]``

:说明:

  事件处理状态 State 类型
"""
T_StateFactory = Callable[["Message"], Awaitable[T_State]]
"""
:类型: ``Callable[[Message], Awaitable[T_State]]``

:说明:

  事件处理状态 State 类工厂函数
"""
T_RuleChecker = Callable[["Message"], Union[bool,
                                            Awaitable[bool]]]

T_Handler = Union[
    Callable[[Any, Any], Union[Awaitable[None], Awaitable[NoReturn]]],
    Callable[[Any], Union[Awaitable[None], Awaitable[NoReturn]]]
]
"""
:类型:

  * ``Callable[[Message, T_State], Union[Awaitable[None], Awaitable[NoReturn]]]``
  * ``Callable[[Message], Union[Awaitable[None], Awaitable[NoReturn]]]``

:说明:

  Handler 即事件的处理函数。
"""
T_ArgsParser = Callable[["Message", T_State], Union[Awaitable[None],
                                                    Awaitable[NoReturn]]]
"""
:类型: ``Callable[[Message, T_State], Union[Awaitable[None], Awaitable[NoReturn]]]``

:说明:

  ArgsParser 即消息参数解析函数，在 Matcher.got 获取参数时被运行。
"""
T_TypeUpdater = Callable[["Message", T_State, str], Awaitable[str]]
"""
:类型: ``Callable[[Message, T_State, str], Awaitable[str]]``

:说明:

  TypeUpdater 在 Matcher.pause, Matcher.reject 时被运行，用于更新响应的事件类型。默认会更新为 ``message``。
"""

T_EventPreProcessor = Callable[["Message", T_State], Awaitable[None]]
"""
:类型: ``Callable[[Message, T_State], Awaitable[None]]``

:说明:

  事件预处理函数 EventPreProcessor 类型
"""
T_EventPostProcessor = Callable[["Message", T_State], Awaitable[None]]
"""
:类型: ``Callable[[Message, T_State], Awaitable[None]]``

:说明:

  事件预处理函数 EventPostProcessor 类型
"""
T_RunPreProcessor = Callable[["Matcher", "Message", T_State],
                             Awaitable[None]]
"""
:类型: ``Callable[[Matcher, Message, T_State], Awaitable[None]]``

:说明:

  事件响应器运行前预处理函数 RunPreProcessor 类型
"""
T_RunPostProcessor = Callable[
    ["Matcher", Optional[Exception], "Message", T_State], Awaitable[None]]
"""
:类型: ``Callable[[Matcher, Optional[Exception], Message, T_State], Awaitable[None]]``

:说明:

  事件响应器运行前预处理函数 RunPostProcessor 类型，第二个参数为运行时产生的错误（如果存在）
"""
