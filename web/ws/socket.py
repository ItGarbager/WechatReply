import asyncio
import json
import traceback
from abc import ABC

import tornado.websocket
from tornado.options import define

from wechat import get_friends, WXFriend, START_TIME, logger, WX, Message

define("port", default=3000, help="run on the given port", type=int)

all_user_collections = set()


class UpdateWebSocket(tornado.websocket.WebSocketHandler, ABC):
    # 检查跨域请求，容许跨域，则直接return True，不然自定义筛选条件
    def check_origin(self, origin):
        return True

    # 创建链接的时候，把用户保存到字典里面，用于后续推送消息使用
    def open(self):
        logger.info("client %s opened" % id(self))

        # 初始化
        all_user_collections.add(self)

    # 关闭链接的时候须要清空链接用户
    def on_close(self):
        logger.info("client %s closed" % (id(self)))

        all_user_collections.remove(self)
        try:
            self.close()
        except:
            logger.info('close failed')

    def on_message(self, message):
        # 接收客户端发来的消息
        try:
            # 获取消息json
            message = json.loads(message)
            logger.info('get client message %s' % message)

            # 获取回调函数以及参数
            send_type = message.get('send_type')
            args = message.get('args')
            kwargs = message.get('kwargs')

            # 判断回调函数是否存在
            if hasattr(WX(), send_type):
                logger.info('send_type %s' % send_type)
                getattr(WX(), send_type)(*args, **kwargs)
            else:
                logger.warning('send_type %s not exists' % send_type)
        except Exception as e:
            logger.info('message error %s' % e)

    @classmethod
    def send_message(cls, message):
        asyncio.set_event_loop(asyncio.new_event_loop())

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

                    if all_user_collections:
                        logger.info('message: %s' % message)
                    else:
                        logger.warning('haven\'t user_collections')
                    for collection in all_user_collections:
                        logger.info('collection %s' % id(collection))

                        message = json.dumps(Message(data, chat_type, group, user, msg).__dict__)
                        collection.write_message(message)

        except Exception:
            logger.info('on_message monitor failed %s' % traceback.print_exc())
