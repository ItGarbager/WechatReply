import threading

from monitor.logger import logger
from monitor.plugin import load_plugins, load_builtin_plugin
from web.http import Application
from wechat import WX
from wechat.tasks.schedulers import scheduler


def main():
    app = Application(logger=logger)
    # 加载内置插件 ping
    load_builtin_plugin('echo')
    # 加载自定义微信机器人插件
    load_plugins('wechat/plugins')

    objs = [WX(), app, scheduler]
    for obj in objs:
        _ = threading.Thread(target=obj.start, args=tuple())
        _.start()


if __name__ == '__main__':
    main()
