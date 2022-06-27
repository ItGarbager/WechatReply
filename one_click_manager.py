import threading

from web.http import Application
from monitor.logger import logger
from monitor.plugins import load_plugins
from wechat.tasks.schedulers import scheduler
from wechat import WX


def main():
    app = Application(logger=logger)

    # 加载微信机器人插件
    load_plugins('wechat/plugins')

    objs = [WX(), app, scheduler]
    for obj in objs:
        _ = threading.Thread(target=obj.start, args=tuple())
        _.start()


if __name__ == '__main__':
    main()
