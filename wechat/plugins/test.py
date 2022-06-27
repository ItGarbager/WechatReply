import pprint

from monitor.plugin import on_regex, on_full_match

test = on_regex(pattern=r'(.+)天气(.+)差')


@test.handle()
async def _(message):
    pprint.pprint(message.data)


test2 = on_full_match(msg='必须全文匹配才能响应')


@test2.handle()
async def _(message):
    pprint.pprint(message.__dict__)
