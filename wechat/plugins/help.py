from monitor.plugins import on_command

_help = on_command(cmd='菜单', aliases={'功能', '帮助'})


@_help.handle()
async def _(message):
    friend = message.group or message.user
    message.wx.send_text(friend, '''
    当前功能：
    1. 自动回复
    2. 任务添加
    3. 每日签到
    
    ''')
