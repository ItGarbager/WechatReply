from flask import Flask
from web.app.routers import wechat_app


class Application:
    app = Flask(__name__)

    def __init__(self):
        self.__load_routers()

    def __load_routers(self):
        # 加载所有的二级路由APP
        self.app.register_blueprint(blueprint=wechat_app)

    def start(self, host='127.0.0.1', port=5741, debug=False):
        self.app.run(host=host, port=port, debug=debug)
