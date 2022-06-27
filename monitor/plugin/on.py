"""本模块定义事件响应器便携定义函数。
FrontMatter:
    sidebar_position: 2
    description: monitor.plugin.monitor 模块
"""
import inspect
import re
from argparse import ArgumentParser
from types import ModuleType
from typing import Any, Set, Dict, List, Type, Tuple, Union, Optional

from .manager import _current_plugin
from ..dependencies import Dependent
from ..matcher import Matcher
from ..rule import (
    Rule,
    regex,
    command,
    keyword,
    endswith,
    startswith,
    full_match,
)
from ..typing import T_Handler, T_RuleChecker


def _store_matcher(matcher: Type[Matcher]) -> None:
    plugin = _current_plugin.get()
    # only store the matcher defined in the plugin
    if plugin:
        plugin.matcher.add(matcher)


def _get_matcher_module(depth: int = 1) -> Optional[ModuleType]:
    current_frame = inspect.currentframe()
    if current_frame is None:
        return None
    frame = inspect.getouterframes(current_frame)[depth + 1].frame
    split_list = re.split(r'\s+', str(inspect.getmodule(frame)))
    if len(split_list) >= 2:
        return split_list[1]
    return inspect.getmodule(frame)


def on(
        type: str = "",
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        *,
        handlers: Optional[List[Union[T_Handler, Dependent]]] = None,
        temp: bool = False,
        priority: int = 1,
        block: bool = False,
        _depth: int = 0,
) -> Type[Matcher]:
    """
    注册一个基础事件响应器，可自定义类型。
    参数:
        type: 事件响应器类型
        rule: 事件响应规则
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
    """
    matcher = Matcher.new(
        type,
        Rule() & rule,
        temp=temp,
        priority=priority,
        block=block,
        handlers=handlers,
        module=_get_matcher_module(_depth + 1),
    )
    _store_matcher(matcher)
    return matcher


def on_message(
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        *,
        handlers: Optional[List[Union[T_Handler, Dependent]]] = None,
        temp: bool = False,
        priority: int = 1,
        block: bool = True,
        _depth: int = 0,
) -> Type[Matcher]:
    """
    注册一个消息事件响应器。
    参数:
        rule: 事件响应规则
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
    """
    matcher = Matcher.new(
        "message",
        Rule() & rule,
        temp=temp,
        priority=priority,
        block=block,
        handlers=handlers,
        module=_get_matcher_module(_depth + 1),
    )
    _store_matcher(matcher)

    return matcher


def on_startswith(
        msg: Union[str, Tuple[str, ...]],
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        chat_type: Optional[Union[str, None]] = None,
        ignore_case: bool = False,
        _depth: int = 0,
        **kwargs,
) -> Type[Matcher]:
    """
    注册一个消息事件响应器，并且当消息的**文本部分**以指定内容开头时响应。
    参数:
        chat_type: 消息类型，chatroom|person, 不填两者都会监听
        msg: 指定消息开头内容
        rule: 事件响应规则
        ignore_case: 是否忽略大小写
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
    """
    return on_message(startswith(chat_type, msg, ignore_case) & rule, **kwargs, _depth=_depth + 1)


def on_endswith(
        msg: Union[str, Tuple[str, ...]],
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        chat_type: Optional[Union[str, None]] = None,
        ignore_case: bool = False,
        _depth: int = 0,
        **kwargs,
) -> Type[Matcher]:
    """
    注册一个消息事件响应器，并且当消息的**文本部分**以指定内容结尾时响应。
    参数:
        chat_type: 消息类型，chatroom|person, 不填两者都会监听
        msg: 指定消息结尾内容
        rule: 事件响应规则
        ignore_case: 是否忽略大小写
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
    """
    return on_message(endswith(chat_type, msg, ignore_case) & rule, **kwargs, _depth=_depth + 1)


def on_full_match(
        msg: Union[str, Tuple[str, ...]],
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        chat_type: Optional[Union[str, None]] = None,
        ignore_case: bool = False,
        _depth: int = 0,
        **kwargs,
) -> Type[Matcher]:
    """
    注册一个消息事件响应器，并且当消息的**文本部分**与指定内容完全一致时响应。
    参数:
        chat_type: 消息类型，chatroom|person, 不填两者都会监听
        msg: 指定消息全匹配内容
        rule: 事件响应规则
        ignore_case: 是否忽略大小写
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
    """
    return on_message(full_match(chat_type, msg, ignore_case) & rule, **kwargs, _depth=_depth + 1)


def on_keyword(
        keywords: Set[str],
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        chat_type: Optional[Union[str, None]] = None,
        _any: bool = True,
        _depth: int = 0,
        **kwargs,
) -> Type[Matcher]:
    """
    注册一个消息事件响应器，并且当消息纯文本部分包含关键词时响应。
    参数:
        chat_type: 消息类型，chatroom|person, 不填两者都会监听
        keywords: 关键词列表
        _any: 与或关系，存在还是全部
        rule: 事件响应规则
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
    """
    return on_message(keyword(chat_type, *keywords, _any=_any) & rule, **kwargs, _depth=_depth + 1)


def on_command(
        cmd: Union[str, Tuple[str, ...]],
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        chat_type: Optional[Union[str, None]] = None,
        aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
        _depth: int = 0,
        **kwargs,
) -> Type[Matcher]:
    """
    注册一个消息事件响应器，并且当消息以指定命令开头时响应。
    命令匹配规则参考: `命令形式匹配 <rule.md#command-command>`_
    参数:
        chat_type: 消息类型，chatroom|person, 不填两者都会监听
        cmd: 指定命令内容
        rule: 事件响应规则
        aliases: 命令别名
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
    """

    commands = set([cmd]) | (aliases or set())
    block = kwargs.pop("block", False)
    return on_message(
        command(chat_type, *commands) & rule, block=block, **kwargs, _depth=_depth + 1
    )


def on_regex(
        pattern: str,
        flags: Union[int, re.RegexFlag] = 0,
        chat_type: Optional[Union[str, None]] = None,
        rule: Optional[Union[Rule, T_RuleChecker]] = None,
        _depth: int = 0,
        **kwargs,
) -> Type[Matcher]:
    """
    注册一个消息事件响应器，并且当消息匹配正则表达式时响应。
    命令匹配规则参考: `正则匹配 <rule.md#regex-regex-flags-0>`_
    参数:
        chat_type: 消息类型，chatroom|person, 不填两者都会监听
        pattern: 正则表达式
        flags: 正则匹配标志
        rule: 事件响应规则
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
    """
    return on_message(regex(chat_type, pattern, flags) & rule, **kwargs, _depth=_depth + 1)
