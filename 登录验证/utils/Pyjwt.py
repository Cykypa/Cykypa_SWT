import datetime
import json

import jwt

# 密钥
SECRET_KEY = '0okmniu98uhbvgy7'


def response(data, code, message):
    return json.dumps({
        'data': data,
        'code': code,
        'message': message
    }, indent=2, ensure_ascii=False)


class Jwt:
    @staticmethod
    def jwtEncode(data):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=1),
                'iat': datetime.datetime.utcnow(),
                'iss': 'sirius',
                'data': {
                    'username': data['username'],
                    'role': data['role']
                }
            }
            return jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def jwtDecode(token):
        try:
            # 指定加密算法，
            payload = jwt.decode(token, SECRET_KEY, options={'verify_exp': True}, algorithms=['HS256'])
            print(payload, "payload")
            if 'data' in payload and 'username' in payload['data']:
                return payload['data']
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 50014
        except jwt.InvalidTokenError:
            return 50008

    @staticmethod
    def authHeader(request):
        token = request.headers.get('X-Token')
        p = Jwt.jwtDecode(token)
        if p == 50008:
            return response({}, code=50008, message='非法token！')
        elif p == 50014:
            return response({}, code=50014, message='过期token！')
        else:
            return response(p, code=20000, message='验证通过！')
        # return response(p, code=20000, message='验证通过！')
