import logging
import time

from WechatPCAPI import WechatPCAPI

logging.basicConfig(level=logging.INFO)


# 单例模式
def singleton(cls, *args, **kw):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


class WXFriend:
    person = {}
    chatroom = {}
    gh = {}


@singleton
class WxINFO:
    friend = WXFriend


@singleton
class WX:
    def __init__(self, on_message):
        self.wx = WechatPCAPI(on_message=on_message, log=logging)

    def start(self):
        self.wx.start_wechat(block=True)
        while not self.wx.get_myself():
            time.sleep(5)

        logging.info('登陆成功')

        time.sleep(10)

    def send_text(self, *args, **kwargs):
        self.wx.send_text(*args, **kwargs)
