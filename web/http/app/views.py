import json

from flask import views, request, Response, stream_with_context

from web.http.utils import global_response
from wechat import WXFriend, WX


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
        WX().send_text(friend_id, msg=msg)

    return global_response(data={'friend_id': friend_id, 'send_msg': msg}, msg='Message Send Successful')


class GetInfo(views.MethodView):
    # 可省略
    methods = ["GET", "POST"]

    def get(self, friend_type):
        return global_response(data=getattr(WXFriend, friend_type), msg='Get Friends\'s Info Success')

    def post(self, friend_type):
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            json_data = request.json

        elif 'form-data' in content_type:
            json_data = request.form

        else:
            return global_response(status=400)
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
