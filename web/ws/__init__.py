#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from collections.abc import AsyncIterable
from typing import Set

import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado.options import options

from web.ws.socket import UpdateWebSocket


class Users(AsyncIterable, Set):
    pass


class WSApplication(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", UpdateWebSocket)]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)

    def start(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        tornado.options.parse_command_line()
        self.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
