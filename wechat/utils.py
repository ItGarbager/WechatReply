import warnings

warnings.filterwarnings('ignore')


def get_friends(message, WXFriend):
    """
    获取通讯录信息
    :param message: 回调消息
    :return: 空 | 格式化后的用户信息
    """
    # message dict
    msg_type = message.get('type')
    data = message.get('data')
    # 处理业务逻辑

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
                getattr(WXFriend, friend_type)[_id] = {'name': _name, 'type': friend_type,
                                                       'remark_name': remark_name}
        else:
            chat_type = msg_type.rsplit('::', 1)[-1]
            group = data.get('from_chatroom_wxid')
            user = data.get('from_member_wxid', data.get('from_wxid'))
            msg = data.get('msg')

            return data, chat_type, group, user, msg
