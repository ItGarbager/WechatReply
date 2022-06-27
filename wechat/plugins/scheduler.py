from re import split

from wechat import Message
from monitor.plugin import on_command
from wechat.tasks.schedulers import add_task

# 命令类型的时间响应器
schedule = on_command(cmd='添加定时', aliases={'添加任务', '添加定时任务'})

# 任务映射表
task_map_dict = {
    '发送文本消息': 'send_text',
    'send_text': 'send_text'
}


@schedule.handle()
async def _(message: Message):
    command = message.data.get('command')
    if command:
        prefix = command.get('prefix')
        others = command.get('others')
        friend = message.group or message.user
        if others and len(others) == 4:
            call, date, send_friend, msg = others
            call = task_map_dict.get(call)
            if call:
                if ':' in date and date.replace(':', '').isdigit():
                    hour, minute = split(r'[:：]', date)
                    message.wx.send_text(friend, '定时任务添加成功')
                    if send_friend == '-':
                        send_friend = friend
                    add_task(task_map_dict[call], hour, minute, *(message.wx, send_friend, msg))
                else:
                    message.wx.send_text(friend, '时间格式异常')
            else:
                message.wx.send_text(friend, '任务类型不存在')
        else:
            message.wx.send_text(friend, '命令格式错误，格式示例:\n'
                                         f'{prefix} 发送文本消息(添加任务类型) 10:10(时间，时:分) xxxxx_yyyy(通讯录id) 发送消息')
