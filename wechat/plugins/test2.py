from wechat.monitor.plugins import on_full_match  # 先导入一个响应器

# 全文匹配响应器， priority 越低优先级越高, block 是否阻断向低优先级传递, 默认为 True
test = on_full_match(msg=('sss', 'bbb'), priority=2, block=False)


@test.handle()
async def _(message):
    print(message.__dict__, 1)


test2 = on_full_match(msg=('sss', 'bbb'), priority=3, block=True)


@test2.handle()
async def _(message):
    print(message.__dict__, 2)


test3 = on_full_match(msg=('sss', 'bbb'), priority=4)


@test3.handle()
async def _(message):
    print(message.__dict__, 3)
