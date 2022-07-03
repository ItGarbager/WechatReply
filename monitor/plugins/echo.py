from ..plugin import on_full_match  # 先导入一个响应器

# 全文匹配响应器， priority 越低优先级越高, block 是否阻断向低优先级传递, 默认为 True
ping = on_full_match(msg=('ping',), priority=1, block=True)


@ping.handle()
async def _(message):
    await ping.finish('pong!')
