import json

from flask import views, request, Response, stream_with_context

from web.http.utils import global_response, get_param
from wechat import WXFriend, WX


def send_text_msg():
    success, json_data = get_param(request)
    if not success:
        return json_data
    msg = json_data.get('msg')
    friend_id = json_data.get('friend_id')
    if msg:
        WX().send_text(friend_id, msg=msg)

    return global_response(data={'friend_id': friend_id, 'send_msg': msg}, msg='Message Send Successful')


class GetInfo(views.MethodView):
    # 可省略
    methods = ["GET", "POST"]

    def get(self, friend_type):
        return global_response(data=getattr(WXFriend, friend_type), msg='Get Friends\'s Info Success')

    def post(self, friend_type):
        success, json_data = get_param(request)
        if not success:
            return json_data
        name = json_data.get('name')
        type_ = json_data.get('type_')
        if name:
            def stream():
                yield '['
                for _, friend in getattr(WXFriend, friend_type).items():
                    if type_:
                        if name in friend.get(type_):
                            friend['_id'] = _
                            yield json.dumps(friend)
                            yield ',\n'
                    else:
                        try:
                            if name in friend['name'] or name in _ or name in friend['remark_name']:
                                friend['_id'] = _
                                yield json.dumps(friend)
                                yield ',\n'
                        except:
                            pass

                yield ']'

            return Response(stream_with_context(stream()), mimetype='application/json')
        else:
            return global_response(data={}, msg='Get ({})\'s Info Failed'.format(name))


class CallBackWechat(views.MethodView):
    """微信接口回调函数"""
    # 可省略
    methods = ["POST"]

    def post(self, function):
        success, json_data = get_param(request)
        if not success:
            return json_data
        if hasattr(WX(), function):
            function = getattr(WX(), function)
            res = function(**json_data)
            print(res)
            if res:
                return global_response(data=res)
        return global_response()
