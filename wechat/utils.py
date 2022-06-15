import logging

import warnings

from wechat import WXFriend, WX

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)


# 这是消息回调函数，所有的返回消息都在这里接收，建议异步处理，防止阻塞
def on_message(message):
    # 回调的数据及其类型
    data = message.get('data')
    msg_type = message.get('type')
    try:
        # 填写监听回调逻辑
        if msg_type:

            if msg_type.startswith('friend::'):  # 通讯录类型
                friend_type = msg_type.rsplit('::', 1)[-1]
                if friend_type == 'person':
                    _id = 'wx'
                    _name = 'wx_nick'
                else:
                    _id = friend_type
                    _name = friend_type + '_'
                if data:
                    _id = data.get('%s_id' % _id)
                    _name = data.get('%sname' % _name)
                    remark_name = data.get('remark_name')

                    # 将通讯录信息传入初始化结构中
                    getattr(WXFriend, friend_type)[_id] = {
                        'name': _name,
                        'type': friend_type,
                        'remark_name': remark_name
                    }
            elif msg_type.startswith('msg::'):  # 消息类型
                # 处理业务逻辑
                pass
    except:
        pass


# 实例化的微信对象
wx = WX(on_message=on_message)
