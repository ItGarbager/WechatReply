import asyncio
import time
import traceback

from WechatPCAPI import WechatPCAPI

from monitor.logger import logger
from monitor.message import handle_event
from wechat.config import START_TIME
from wechat.utils import get_friends


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


def local_on_message(message):
    """
    这是消息回调函数，所有的返回消息都在这里接收，建议异步处理，防止阻塞
    :param message: 回调消息
    :return:
    """
    try:
        res = get_friends(message, WXFriend=WXFriend)

        # 判断是否为通讯录消息
        if res:
            data, chat_type, group, user, msg = res

            # 解析当前消息收发状态
            try:
                send_or_recv = not bool(eval(data.get('send_or_recv', '').split('+', 1)[0]))
            except:
                send_or_recv = False

            # 判断为收取消息并时间大于启动时间才会进行回复
            if send_or_recv and data.get('time') >= START_TIME:
                logger.info('message: %s' % message)
                # 异步启动当前注册的事件响应器，插件目录 wechat/plugins/
                asyncio.run(handle_event(Message(data, chat_type, group, user, msg, WX())))

    except Exception:
        logger.info('on_message monitor failed %s' % traceback.print_exc())


@singleton
class WX:
    def __init__(self, on_message=local_on_message):
        self.wx = WechatPCAPI(on_message=on_message, log=logger)

    def start(self):
        self.wx.start_wechat(block=True)
        while not self.wx.get_myself():
            time.sleep(5)

        logger.info('登陆成功')

        time.sleep(10)

    def send_text(self, *args, **kwargs):
        self.wx.send_text(*args, **kwargs)


class Message:
    def __init__(self, data, chat_type, group, user, msg, wx=None):
        self.data = data
        self.chat_type = chat_type
        self.group = group
        self.user = user
        self.msg = msg
        self.wx = wx
