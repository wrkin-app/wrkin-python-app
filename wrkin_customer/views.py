from wrkin_customer.models import *
from wrkin_customer.helper import getOtpValidator,otpValidator,retryOtpValidator
from custom_jwt import generateJwtToken,verifyJwtToken
#-----------------------query related-------------------------------------------------
from django.db.models import Avg,Count,Case, When, IntegerField,Sum,FloatField,CharField
from django.db.models import F,Func,Q
from django.db.models import Value as V
from django.contrib.auth.hashers import make_password,check_password
# from django.db.models.functions import Concat,Cast,Substr
# from django.db.models import Min, Max
# from django.db.models import Subquery
# from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
#----------------------------restAPI--------------------------------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from rest_framework.decorators import parser_classes
# from rest_framework.parsers import MultiPartParser,FormParser
#---------------------------python----------------------------------------------------
from django.conf import settings
import jwt
from datetime import datetime

# Create your views here.

@api_view(['GET'])
def index(request):
    res = CustomerUser.objects.values()
    return Response(res)

@api_view(['POST'])
def get_otp(request):
    if request.method == 'POST':
        data = request.data
        get_otp_validator = getOtpValidator(data)
        if not get_otp_validator['status']:
            return Response(get_otp_validator)
        otp = 1234
        current_time = datetime.now()
        try:
            otp_obj = OtpVerify.objects.get(country_code = data['country_code'],phone_no = data['phone_no'])
            prev_otp_time = current_time - otp_obj.created_at
            prev_otp_time = prev_otp_time.total_seconds()//60
            if prev_otp_time < 30:
                if otp_obj.try_count < 3:
                    otp = 1234
                    otp_obj.try_count = otp_obj.try_count + 1
                    res = {
                            'status':True,
                            'message':'OTP send successfully',
                            'otp_id':otp_obj.id
                        }
                    return Response(res)
                else:
                    res = {
                            'status':False,
                            'message':f'Account blocked, please try again after {int(30 - prev_otp_time)} minutes or contact support',
                        }
                    return Response(res)
            else:
                otp_obj.delete()
                raise Exception
        except:
            otp_obj = OtpVerify(
                                    country_code = data['country_code'],
                                    phone_no = data['phone_no'],
                                    value = otp,
                                    try_count = 1,
                                    created_at = current_time,
                            )
            otp_obj.save()
            res = {
                    'status':True,
                    'message':'OTP send successfully',
                    'otp_id':otp_obj.id
                }
            return Response(res)

@api_view(['POST'])
def verify_otp(request):
    if request.method == 'POST':
        data = request.data
        otp_validator = otpValidator(data)
        if not otp_validator['status']:
            return Response(otp_validator)
        try:
            otp_obj = OtpVerify.objects.get(id = data['otp_id'])
        except:
            res = {
                    'status':False,
                    'message':'invalid otp_id'
                }
            return Response(res)
        if data['otp'] != otp_obj.value:
            res = {
                    'status':False,
                    'message':'invalid otp'
            }
            return Response(res)
        try:
            cust_obj = CustomerUser.objects.get(country_code = otp_obj.country_code,phone_no = otp_obj.phone_no)
        except:
            res = {
                 'status':False,
                 'message':'something went wrong, please try again'
            }
            return Response(res)
        generate_jwt_token = generateJwtToken(cust_obj.id)
        if generate_jwt_token['status']:
            cust_obj.secure_token = generate_jwt_token['token']
            cust_obj.last_login_at = datetime.now()
            cust_obj.save()
            res = {
                    'status':True,
                    'message':'OTP verified',
                    'token':generate_jwt_token['token']
            }
            otp_obj.delete()
        else:
            res = {
                    'status':True,
                    'message':'something went wrong, please try again'
            }
    
        return Response(res)
@api_view(['POST'])
def retry_otp(request):
    if request.method == 'POST':
        data = request.data
        retry_otp_validator = retryOtpValidator(data)
        if not retry_otp_validator['status']:
            return Response(retry_otp_validator)
        try:
            otp_obj = OtpVerify.objects.get(id=data['otp_id'])
        except:
            res = {
                    'status':False,
                    'message':'otp object not found for this number'
            }
            return Response(res)
        current_time = datetime.now()
        prev_otp_time = current_time - otp_obj.created_at
        prev_otp_time = prev_otp_time.total_seconds()//60
        if otp_obj.try_count == 3:
            res = {
                    'status':False,
                    'message':f'Account blocked, please try again after {int(30 - prev_otp_time)} minutes or contact support',
                }
            return Response(res)
        new_otp = 1234
        otp_obj.try_count = otp_obj.try_count + 1
        otp_obj.value = new_otp
        #send otp function
        otp_obj.save()
        res = {
                'status':True,
                'message':'otp resent successfull'
        }
        return Response(res)

        
            
        
        