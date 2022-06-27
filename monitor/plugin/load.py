"""本模块定义插件加载接口。
FrontMatter:
    sidebar_position: 1
    description: monitor.plugin.load 模块
"""
import json
from typing import Set, Iterable, Optional

from . import _managers
from .manager import PluginManager
from .plugin import Plugin


def load_plugin(module_path: str) -> Optional[Plugin]:
    """加载单个插件，可以是本地插件或是通过 `pip` 安装的插件。
    参数:
        module_path: 插件名称 `path.to.your.plugin`
    """

    manager = PluginManager([module_path])
    _managers.append(manager)
    return manager.load_plugin(module_path)


def load_plugins(*plugin_dir: str) -> Set[Plugin]:
    """导入文件夹下多个插件，以 `_` 开头的插件不会被导入!
    参数:
        plugin_dir: 文件夹路径
    """
    manager = PluginManager(search_path=plugin_dir)

    _managers.append(manager)
    return manager.load_all_plugins()


def load_all_plugins(
        module_path: Iterable[str], plugin_dir: Iterable[str]
) -> Set[Plugin]:
    """导入指定列表中的插件以及指定目录下多个插件，以 `_` 开头的插件不会被导入!
    参数:
        module_path: 指定插件集合
        plugin_dir: 指定文件夹路径集合
    """
    manager = PluginManager(module_path, plugin_dir)
    _managers.append(manager)
    return manager.load_all_plugins()


def load_from_json(file_path: str, encoding: str = "utf-8") -> Set[Plugin]:
    """导入指定 json 文件中的 `plugin` 以及 `plugin_dirs` 下多个插件，以 `_` 开头的插件不会被导入!
    参数:
        file_path: 指定 json 文件路径
        encoding: 指定 json 文件编码
    用法:
        ```json title=plugin.json
        {
            "plugin": ["some_plugin"],
            "plugin_dirs": ["some_dir"]
        }
        ```
        ```python
        wechat_bot.load_from_json("plugin.json")
        ```
    """
    with open(file_path, "r", encoding=encoding) as f:
        data = json.load(f)
    plugins = data.get("plugin")
    plugin_dirs = data.get("plugin_dirs")
    assert isinstance(plugins, list), "plugin must be a list of plugin name"
    assert isinstance(plugin_dirs, list), "plugin_dirs must be a list of directories"
    return load_all_plugins(set(plugins), set(plugin_dirs))


def load_builtin_plugin(name: str) -> Optional[Plugin]:
    """导入 WechatBot 内置插件。
    参数:
        name: 插件名称
    """
    return load_plugin(f"monitor.plugins.{name}")


def load_builtin_plugins(*plugins: str) -> Set[Plugin]:
    """导入多个 WechatBot 内置插件。
    参数:
        plugin: 插件名称列表
    """
    return load_all_plugins([f"monitor.plugins.{p}" for p in plugins], [])


def _find_manager_by_name(name: str) -> Optional[PluginManager]:
    for manager in reversed(_managers):
        if name in manager.plugins or name in manager.searched_plugins:
            return manager
