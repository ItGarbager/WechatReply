from monitor.plugins import on_keyword
from wechat.tasks.call_back import do

s = on_keyword(keywords={'#接龙', '健康上报'}, _any=False, priority=1)


@s.handle()
async def solitaire(message):
    if message.group in (
            '20940824326@chatroom', '17817852482@chatroom') and '赵林旭' not in message.msg and message.msg.count(
        '王红艳') == 1 and message.user in (
            'wxid_pol0ftktwz1922', 'why35767539'):
        await do(message.group)
