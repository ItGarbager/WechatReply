from wechat.monitor.plugins.on import on_keyword
from wechat import Message

# priority 为优先级，数值越低优先级越高，block 是否阻断消息继续传递，默认 True，为 False 时还需继续传递至下一层事件处理
hello = on_keyword(keywords={'hello', '你好', '早'}, priority=2, block=False)


@hello.handle()
async def hello(message: Message):
    if message.group:
        message.wx.send_text(message.group, '你好')
    else:
        message.wx.send_text(message.user, 'hello')


hello2 = on_keyword(keywords={'hello', '你好', '早'}, priority=1)


@hello2.handle()
async def hello2(message: Message):
    if message.group:
        message.wx.send_text(message.group, '你好2')
    else:
        message.wx.send_text(message.user, 'hello2')
