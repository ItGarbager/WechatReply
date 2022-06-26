import asyncio

from flask import Flask
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from web.app.routers import wechat_app


class Application:
    app = Flask(__name__)

    def __init__(self, logger=None):
        self.__load_routers()
        self.logger = logger

    def __load_routers(self):
        # 加载所有的二级路由APP
        self.app.register_blueprint(blueprint=wechat_app)

    def start(self, port=5741):
        asyncio.set_event_loop(asyncio.new_event_loop())
        http_server = HTTPServer(WSGIContainer(self.app))
        http_server.listen(port)
        IOLoop.instance().start()
