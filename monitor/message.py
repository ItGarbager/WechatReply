"""
事件处理
========

Monitor 内部处理并按优先级分发事件给所有事件响应器，提供了多个插槽以进行事件的预处理等。
"""

import asyncio
from typing import Set, Type, TYPE_CHECKING

from .exception import IgnoredException, StopPropagation
from .logger import logger
from .matcher import matchers, Matcher
from .rule import TrieRule
from .typing import T_EventPreProcessor, T_RunPreProcessor, T_EventPostProcessor, T_RunPostProcessor, T_State

if TYPE_CHECKING:
    from classes import Message

_event_preprocessors: Set[T_EventPreProcessor] = set()
_event_postprocessors: Set[T_EventPostProcessor] = set()
_run_preprocessors: Set[T_RunPreProcessor] = set()
_run_postprocessors: Set[T_RunPostProcessor] = set()


def event_preprocessor(func: T_EventPreProcessor) -> T_EventPreProcessor:
    """
    :说明:

      事件预处理。装饰一个函数，使它在每次接收到事件并分发给各响应器之前执行。

    :参数:

      事件预处理函数接收三个参数。

      * ``bot: Bot``: Bot 对象
      * ``event: Event``: Event 对象
      * ``state: T_State``: 当前 State
    """
    _event_preprocessors.add(func)
    return func


def event_postprocessor(func: T_EventPostProcessor) -> T_EventPostProcessor:
    """
    :说明:

      事件后处理。装饰一个函数，使它在每次接收到事件并分发给各响应器之后执行。

    :参数:

      事件后处理函数接收三个参数。

      * ``bot: Bot``: Bot 对象
      * ``event: Event``: Event 对象
      * ``state: T_State``: 当前事件运行前 State
    """
    _event_postprocessors.add(func)
    return func


def run_preprocessor(func: T_RunPreProcessor) -> T_RunPreProcessor:
    """
    :说明:

      运行预处理。装饰一个函数，使它在每次事件响应器运行前执行。

    :参数:

      运行预处理函数接收四个参数。

      * ``matcher: Matcher``: 当前要运行的事件响应器
      * ``bot: Bot``: Bot 对象
      * ``event: Event``: Event 对象
      * ``state: T_State``: 当前 State
    """
    _run_preprocessors.add(func)
    return func


def run_postprocessor(func: T_RunPostProcessor) -> T_RunPostProcessor:
    """
    :说明:

      运行后处理。装饰一个函数，使它在每次事件响应器运行后执行。

    :参数:

      运行后处理函数接收五个参数。

      * ``matcher: Matcher``: 运行完毕的事件响应器
      * ``exception: Optional[Exception]``: 事件响应器运行错误（如果存在）
      * ``bot: Bot``: Bot 对象
      * ``event: Event``: Event 对象
      * ``state: T_State``: 当前 State
    """
    _run_postprocessors.add(func)
    return func


async def _check_matcher(priority: int, Matcher: Type[Matcher], message: "Message", state: T_State) -> None:
    try:
        if not await Matcher.check_rule(message, state):
            return
    except Exception as e:
        logger.opt(colors=True, exception=e).error(
            f"<r><bg #f8bbd0>Rule check failed for {Matcher}.</bg #f8bbd0></r>")
        return

    if Matcher.temp:
        try:
            matchers[priority].remove(Matcher)
        except Exception:
            pass

    await _run_matcher(Matcher, message, state)


async def _run_matcher(Matcher: Type[Matcher], message: "Message", state: T_State) -> None:
    logger.info(f"Event will be handled by {Matcher}")

    matcher = Matcher()

    coros = list(
        map(lambda x: x(matcher, message, state), _run_preprocessors))
    if coros:
        try:
            await asyncio.gather(*coros)
        except IgnoredException:
            logger.opt(colors=True).info(
                f"Matcher {matcher} running is <b>cancelled</b>")
            return
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                "<r><bg #f8bbd0>Error when running RunPreProcessors. "
                "Running cancelled!</bg #f8bbd0></r>")
            return

    exception = None

    try:
        logger.debug(f"Running matcher {matcher}")
        await matcher.run(message, state)
    except Exception as e:
        logger.opt(colors=True, exception=e).error(
            f"<r><bg #f8bbd0>Running matcher {matcher} failed.</bg #f8bbd0></r>"
        )
        exception = e

    coros = list(
        map(lambda x: x(matcher, exception, message, state),
            _run_postprocessors))
    if coros:
        try:
            await asyncio.gather(*coros)
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                "<r><bg #f8bbd0>Error when running RunPostProcessors</bg #f8bbd0></r>"
            )

    if matcher.block:
        raise StopPropagation
    return


async def handle_event(message: "Message"):
    """
    处理一个事件。调用该函数以实现分发事件。
    :param message: 回调消息
    :return:
    :示例:
    .. code-block:: python

        import asyncio
        asyncio.create_task(handle_event(bot, event))

    """
    state = {}
    coros = list(map(lambda x: x(message, state), _event_preprocessors))
    if coros:
        try:
            logger.debug("Running PreProcessors...")
            await asyncio.gather(*coros)
        except IgnoredException:
            return
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                "<r><bg #f8bbd0>Error when running EventPreProcessors. "
                "Event ignored!</bg #f8bbd0></r>")
            return
    # Trie Match
    _, _ = TrieRule.get_value(message, state)

    break_flag = False

    for priority in sorted(matchers.keys()):

        if break_flag:
            break

        pending_tasks = [
            _check_matcher(priority, matcher, message, state)
            for matcher in matchers[priority]
        ]
        results = await asyncio.gather(*pending_tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, StopPropagation):
                if not break_flag:
                    break_flag = True
                    logger.debug("Stop event propagation")

    coros = list(map(lambda x: x(message, state), _event_postprocessors))
    if coros:
        try:
            logger.debug("Running PostProcessors...")
            await asyncio.gather(*coros)
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                "<r><bg #f8bbd0>Error when running EventPostProcessors</bg #f8bbd0></r>"
            )
