from typing import Any

from pydantic.fields import ModelField


class MonitorException(Exception):
    """
    :说明:

      所有 Monitor 发生的异常基类。
    """
    pass


# Processor Exception
class ProcessException(MonitorException):
    """事件处理过程中发生的异常基类。"""


class IgnoredException(ProcessException):
    """指示 Monitor 应该忽略该事件。可由 PreProcessor 抛出。
    参数:
        reason: 忽略事件的原因
    """

    def __init__(self, reason: Any):
        self.reason: Any = reason

    def __repr__(self):
        return f"<IgnoredException, reason={self.reason}>"

    def __str__(self):
        return self.__repr__()


class SkippedException(ProcessException):
    """指示 Monitor 立即结束当前 `Dependent` 的运行。
    例如，可以在 `Handler` 中通过 {ref}`wechat_bot.matcher.Matcher.skip` 抛出。
    用法:
        ```python
        def always_skip():
            Matcher.skip()
        @matcher.handle()
        async def handler(dependency = Depends(always_skip)):
            # never run
        ```
    """


class TypeMisMatch(SkippedException):
    """当前 `Handler` 的参数类型不匹配。"""

    def __init__(self, param: ModelField, value: Any):
        self.param: ModelField = param
        self.value: Any = value

    def __repr__(self):
        return f"<TypeMisMatch, param={self.param}, value={self.value}>"

    def __str__(self):
        self.__repr__()


class PausedException(MonitorException):
    """
    :说明:

      指示 NoneBot 结束当前 ``Handler`` 并等待下一条消息后继续下一个 ``Handler``。
      可用于用户输入新信息。

    :用法:

      可以在 ``Handler`` 中通过 ``Matcher.pause()`` 抛出。
    """
    pass


class RejectedException(MonitorException):
    """
    :说明:

      指示 NoneBot 结束当前 ``Handler`` 并等待下一条消息后重新运行当前 ``Handler``。
      可用于用户重新输入。

    :用法:

      可以在 ``Handler`` 中通过 ``Matcher.reject()`` 抛出。
    """
    pass


class FinishedException(MonitorException):
    """
    :说明:

      指示 NoneBot 结束当前 ``Handler`` 且后续 ``Handler`` 不再被运行。
      可用于结束用户会话。

    :用法:

      可以在 ``Handler`` 中通过 ``Matcher.finish()`` 抛出。
    """
    pass


class StopPropagation(MonitorException):
    """
    :说明:

      指示 Monitor 终止事件向下层传播。

    :用法:

      在 ``Matcher.block == True`` 时抛出。
    """
    pass


class NoLogException(Exception):
    """
    :说明:

      指示 Monitor 对当前 ``Event`` 进行处理但不显示 Log 信息，可在 ``get_log_string`` 时抛出
    """
    pass
