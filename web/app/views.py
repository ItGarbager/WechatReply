import _ctypes
from flask import request

from web.utils.funtions import global_response
from wechat import WXFriend

from wechat.utils import wx


def send_text_msg():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json_data = request.json

    elif 'form-data' in content_type:
        json_data = request.form

    else:
        return global_response(status=400)

    msg = json_data.get('msg')
    friend_id = json_data.get('friend_id')
    if msg:
        wx.send_text(friend_id, msg=msg)
    return global_response(data={'friend_id': friend_id, 'send_msg': msg}, msg='Message Send Successful')


def get_info(friend_type):
    return global_response(data=getattr(WXFriend, friend_type), msg='Get Friends\'s Info Successful')
