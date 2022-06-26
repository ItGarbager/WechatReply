from wechat import WX


def send_text(friend_id, msg):
    WX().send_text(friend_id, msg)

