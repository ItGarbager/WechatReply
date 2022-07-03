from monitor.config import TULING_API_KEY, TULING_URL
from monitor.plugin import on_regex

tuling = on_regex(r'.+', rule=to_me(), priority=6)
tuling.__doc__ = '智能聊天'
# 异常回复消息元组
Exception_reply = (
    '我现在还不太明白你在说什么呢，但没关系，以后的我会变得更强呢！',
    '我有点看不懂你的意思呀，可以跟我聊些简单的话题嘛',
    '其实我不太明白你的意思……',
    '抱歉哦，我现在的能力还不能够明白你在说什么，但我会加油的～'
)


# 实现一个接收传入文本， 回复一个图灵响应消息
def get_tuling_reply(user_id, msg):
    request_json = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": msg  # 我们发送的消息
            },
        },
        "userInfo": {
            "apiKey": TULING_API_KEY,  # 图灵机器人官网中获得的apikey
            "userId": user_id  # qq 号
        }
    }
    response = requests.post(url=TULING_URL, json=request_json)
    if response.status_code != 200:  # 判断 是否正常返回
        raise Exception(Exception_reply)

    res_json = response.json()  # 转json
    results = res_json.get('results')
    if not results:
        raise Exception(Exception_reply)
    result = results[0]
    result_type = result.get('resultType')
    if result_type != 'text':
        raise Exception(Exception_reply)

    values = result.get('values')

    reply_msg = values.get('text')
    if not reply_msg:
        raise Exception(Exception_reply)

    return reply_msg


@tuling.handle()
async def _(message, state):
    msg = state['_matched']  # 获取到全匹配字符串

    reply_msg = get_tuling_reply(user_id=message.group, msg=msg)  # 调用自定义回复函数
    await tuling.finish(reply_msg)
