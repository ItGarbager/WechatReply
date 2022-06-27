import threading

from monitor.logger import logger
from web.http import Application
from web.ws import WSApplication
from web.ws.socket import UpdateWebSocket
from wechat import WX

if __name__ == "__main__":
    objs = [WX(on_message=UpdateWebSocket.send_message), WSApplication(), Application(logger=logger)]
    for obj in objs:
        _ = threading.Thread(target=obj.start, args=tuple())
        _.start()
