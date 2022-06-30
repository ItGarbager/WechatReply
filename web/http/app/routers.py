# APP对应路由
# 导入蓝图（Blueprint)
from flask import Blueprint

# 使用蓝图创建一个app对象 url_prefix 为设置url前缀
from web.http.app.views import send_text_msg, GetInfo, CallBackWechat

wechat_app = Blueprint('wechat_app', __name__, url_prefix='/wechat')
wechat_app.add_url_rule('/message/to', None, send_text_msg, methods=['POST'])
wechat_app.add_url_rule('/friends/<friend_type>', None, GetInfo.as_view("get_info"), methods=['GET', 'POST'])
wechat_app.add_url_rule('/callback/<function>', None, CallBackWechat.as_view("callback_wechat"), methods=['POST'])
