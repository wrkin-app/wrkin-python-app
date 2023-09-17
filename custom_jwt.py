import jwt
from datetime import datetime
from django.conf import settings

def generateJwtToken(user_id):
    # Define the payload
    payload = {
        'user_id': user_id,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    res = {
            'status':True,
            'token':token
    }
    return res


def verifyJwtToken(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        res = {
                'status':True,
                'data':payload
        }
        return res
    except jwt.ExpiredSignatureError:
        res = {
                'status':False,
                'message':'invalid signature'
        }
        return res
    except jwt.InvalidTokenError:
        res = {
                'status':False,
                'message':'invalid token'
            }
        return res