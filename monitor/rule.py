"""
规则
====

每个事件响应器 ``Matcher`` 拥有一个匹配规则 ``Rule`` ，其中是 **异步** ``RuleChecker`` 的集合，只有当所有 ``RuleChecker`` 检查结果为 ``True`` 时继续运行。

\:\:\:tip 提示
``RuleChecker`` 既可以是 async function 也可以是 sync function，但在最终会被 ``wechat_bot.utils.run_sync`` 转换为 async function
\:\:\:
"""

import asyncio
import re
from typing import Union, Optional, Callable, NoReturn, Awaitable, Tuple, Set

from .typing import T_RuleChecker
from .utils import run_sync
from .config import CMD_SEP, CMD_START


class Rule:
    """
    说明:

      ``Matcher`` 规则类，当事件传递时，在 ``Matcher`` 运行前进行检查。

    示例:

    code-block:: python

        Rule(async_function) & sync_function
        # 等价于
        from wechat_bot.utils import run_sync
        Rule(async_function, run_sync(sync_function))
    """
    __slots__ = ("checkers",)

    def __init__(
            self, *checkers: Callable[["Message"],
                                      Awaitable[bool]]) -> None:
        """
        异步 RuleChecker
        :param checkers: Callable[[Bot, Event, T_State], Awaitable[bool]]
        """

        self.checkers = set(checkers)

        """
        :说明:
        
          存储 ``RuleChecker``
        :类型:
        
          * ``Set[Callable[[Bot, Event, T_State], Awaitable[bool]]]``
        """

    async def __call__(self, message) -> bool:
        """
        检查是否符合所有规则
        :param message: 消息对象
        :return: 是否合规
        """

        results = await asyncio.gather(
            *map(lambda c: c(message), self.checkers))

        return all(results)

    def __and__(self, other: Optional[Union["Rule", T_RuleChecker]]) -> "Rule":
        checkers = self.checkers.copy()

        if other is None:
            return self
        elif isinstance(other, Rule):
            checkers |= other.checkers

        elif asyncio.iscoroutinefunction(other):
            checkers.add(other)  # type: ignore
        else:
            checkers.add(run_sync(other))

        return Rule(*checkers)

    def __or__(self, other) -> NoReturn:
        raise RuntimeError("Or operation between rules is not allowed.")


def check_type(chat_type, message):
    if chat_type:
        if chat_type == message.chat_type:
            return True
    else:
        return True


def startswith(chat_type: Union[str, None], msg: str, ignore_case: bool) -> Rule:
    """
    匹配消息开头
    :param chat_type: 消息类型，chatroom|person, 不填两者都会监听
    :param msg: 消息开头字符串
    :param ignore_case: 是否忽略大小写
    :return: Rule
    """

    async def _startswith(message: "Message") -> bool:
        if not check_type(chat_type, message):
            return False
        return (message.msg.casefold() if ignore_case else message.msg).startswith(msg)

    return Rule(_startswith)


def endswith(chat_type: Union[str, None], msg: str, ignore_case: bool) -> Rule:
    """
    匹配消息结尾
    :param chat_type:
    :param msg: 指定消息匹配字符串
    :param ignore_case: 是否忽略大小写
    :return: Rule
    """

    async def _endswith(message: "Message") -> bool:
        if not check_type(chat_type, message):
            return False
        return (message.msg.casefold() if ignore_case else message.msg).endswith(msg)

    return Rule(_endswith)


def full_match(chat_type: Union[str, None], msg: Union[str, Tuple[str, ...]], ignore_case: bool = False) -> Rule:
    """
    完全匹配消息。
    :param chat_type: 消息类型，chatroom|person, 不填两者都会监听
    :param msg: 指定消息全匹配字符串元组
    :param ignore_case: 是否忽略大小写
    :return:
    """
    if isinstance(msg, str):
        msg = (msg,)

    async def _full_match(message: "Message") -> bool:
        if not check_type(chat_type, message):
            return False

        for msg_ in msg:
            if (message.msg.casefold() if ignore_case else message.msg) == msg_:
                return True
        return False

    return Rule(_full_match)


def keyword(chat_type: Union[str, None], *keywords: Set, _any=True) -> Rule:
    """
    匹配消息关键词
    :param chat_type: 消息类型，chatroom|person, 不填两者都会监听
    :param keywords: 消息关键词
    :param _any: 与或关系，存在还是全部
    :return: 
    """

    async def _keyword(message: "Message") -> bool:
        if not check_type(chat_type, message):
            return False

        text = message.msg

        local_list = [
            key in text
            for key in keywords
        ]

        return bool(text and (any(local_list) if _any else all(local_list)))

    return Rule(_keyword)


def command(chat_type: Union[str, None], *cmds: Union[str, Tuple[str, ...]]) -> Rule:
    """
    匹配消息命令。
    根据配置里提供的 {ref}``command_start` <wechat_bot.config.Config.command_start>`,
    {ref}``command_sep` <wechat_bot.config.Config.command_sep>` 判断消息是否为命令。
    可以通过 {ref}`wechat_bot.params.Command` 获取匹配成功的命令（例: `("test",)`），
    通过 {ref}`wechat_bot.params.RawCommand` 获取匹配成功的原始命令文本（例: `"/test"`），
    通过 {ref}`wechat_bot.params.CommandArg` 获取匹配成功的命令参数。
    用法:
        使用默认 `command_start`, `command_sep` 配置
        命令 `("test",)` 可以匹配: `/test` 开头的消息
        命令 `("test", "sub")` 可以匹配: `/test.sub` 开头的消息
    :::tip 提示
    命令内容与后续消息间无需空格!
    :::
    :param chat_type: 消息类型，chatroom|person, 不填两者都会监听
    :param cmds: 命令文本或命令元组
    :return: 
    """

    async def _command(message: "Message") -> bool:
        if not check_type(chat_type, message):
            return False
        now_cmds = sorted(cmds, key=len, reverse=True)
        for cmd in now_cmds:
            if isinstance(cmd, tuple):
                cmd = CMD_SEP.join(cmd)

            for start in CMD_START:
                if message.msg.startswith(start + cmd):
                    message.data['command'] = {
                        'prefix': start + cmd,
                        'others': re.split(r' ', message.msg[len(start + cmd):].strip())
                    }
                    return True

        return False

    return Rule(_command)


def regex(chat_type: Union[str, None], pattern: str, flags: Union[int, re.RegexFlag] = 0) -> Rule:
    """
    根据正则表达式进行匹配。

      可以通过 
        message.data["_matched"] = matched.group()
        message.data["_matched_groups"] = matched.groups()
        message.data["_matched_dict"] = matched.groupdict()
      获取正则表达式匹配成功的文本。
    :param chat_type: 消息类型，chatroom|person, 不填两者都会监听
    :param pattern: 正则表达式
    :param flags: 正则标志
    :return: 
    """

    pattern = re.compile(pattern, flags)

    async def _regex(message: "Message") -> bool:
        if not check_type(chat_type, message):
            return False

        matched = pattern.search(message.msg)
        if matched:
            message.data["_matched"] = matched.group()
            message.data["_matched_groups"] = matched.groups()
            message.data["_matched_dict"] = matched.groupdict()
            return True
        else:
            return False

    return Rule(_regex)
