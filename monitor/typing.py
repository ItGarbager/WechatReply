from typing import Any, Union, Callable, NoReturn, Awaitable, Optional, Dict

T_State = Dict[Any, Any]
"""
:类型: ``Dict[Any, Any]``

:说明:

  事件处理状态 State 类型
"""
T_RuleChecker = Callable[["Message"], Union[bool,
                                            Awaitable[bool]]]

T_Handler = Union[Callable[[Any, Any, Any, Any], Union[Awaitable[None],
                                                       Awaitable[NoReturn]]],
                  Callable[[Any, Any, Any], Union[Awaitable[None],
                                                  Awaitable[NoReturn]]],
                  Callable[[Any, Any], Union[Awaitable[None],
                                             Awaitable[NoReturn]]],
                  Callable[[Any], Union[Awaitable[None], Awaitable[NoReturn]]]]
"""
:类型:

  * ``Callable[[Bot, Event, T_State], Union[Awaitable[None], Awaitable[NoReturn]]]``
  * ``Callable[[Bot, Event], Union[Awaitable[None], Awaitable[NoReturn]]]``
  * ``Callable[[Bot, T_State], Union[Awaitable[None], Awaitable[NoReturn]]]``
  * ``Callable[[Bot], Union[Awaitable[None], Awaitable[NoReturn]]]``

:说明:

  Handler 即事件的处理函数。
"""

T_EventPreProcessor = Callable[["Bot", "Event", T_State], Awaitable[None]]
"""
:类型: ``Callable[[Bot, Event, T_State], Awaitable[None]]``

:说明:

  事件预处理函数 EventPreProcessor 类型
"""
T_EventPostProcessor = Callable[["Bot", "Event", T_State], Awaitable[None]]
"""
:类型: ``Callable[[Bot, Event, T_State], Awaitable[None]]``

:说明:

  事件预处理函数 EventPostProcessor 类型
"""
T_RunPreProcessor = Callable[["Matcher", "Bot", "Event", T_State],
                             Awaitable[None]]
"""
:类型: ``Callable[[Matcher, Bot, Event, T_State], Awaitable[None]]``

:说明:

  事件响应器运行前预处理函数 RunPreProcessor 类型
"""
T_RunPostProcessor = Callable[
    ["Matcher", Optional[Exception], "Bot", "Event", T_State], Awaitable[None]]
"""
:类型: ``Callable[[Matcher, Optional[Exception], Bot, Event, T_State], Awaitable[None]]``

:说明:

  事件响应器运行前预处理函数 RunPostProcessor 类型，第二个参数为运行时产生的错误（如果存在）
"""
