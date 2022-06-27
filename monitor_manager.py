import asyncio
import json
import threading
import time

from websocket import create_connection

from monitor.logger import logger
from monitor.message import handle_event
from monitor.plugin import load_plugins, load_builtin_plugin
from wechat import Message
from wechat.tasks.schedulers import scheduler


class Client:

    def __init__(self, url):
        self.url = url
        self.ws = None
        self.connection()

    def connection(self):
        try:
            self.ws = create_connection(self.url)
            logger.success('websocket connection success')

        except ConnectionRefusedError:
            logger.error('websocket connection refuse, reconnecting')
            time.sleep(2)

            self.connection()
        except ConnectionResetError:
            logger.error('websocket connection reset, reconnecting')
            time.sleep(2)

            self.connection()

    def get_recv(self):
        while True:
            try:
                message = self.ws.recv()
                if message:
                    self.__on_message(message)
            except ConnectionResetError:
                self.connection()

    def __on_message(self, message):
        try:
            message = json.loads(message)
            logger.info('get server message %s' % message)
            message['wx'] = self
            asyncio.run(handle_event(Message(**message)))

        except Exception as e:
            logger.error('handle message error %s' % e)

    def send(self, send_type, *args, **kwargs):
        message = json.dumps({
            'send_type': send_type,
            'args': args,
            'kwargs': kwargs
        })
        self.ws.send(message)

    def send_text(self, *args, **kwargs):
        return self.send('send_text', *args, **kwargs)

    def start(self):
        threading.Thread(target=self.get_recv, args=()).start()


if __name__ == '__main__':
    load_builtin_plugin('echo')
    load_plugins('wechat/plugins')
    client = Client('ws://127.0.0.1:3000')
    objs = [client, scheduler]
    for obj in objs:
        _ = threading.Thread(target=obj.start, args=tuple())
        _.start()
