import time

from flask import jsonify

STATUS_CODE_DICT = {
    200: 'Success',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    408: 'Time Out',
    500: 'Internal Server Error',
    502: 'Bad GateWay',
    503: 'Service Unavailable'

}


def global_response(data=None, status=None, msg=None):
    if msg is None:
        if not status:
            status = 200 if data else 404
        msg = STATUS_CODE_DICT.get(status, STATUS_CODE_DICT[status])
    else:
        if not status:
            status = 200

    data = {
        'data': data,
        'msg': msg,
        'status': status,
        'timestamp': time.time()
    }
    return jsonify(data), status
