from wrkin_customer.models import *
from wrkin_customer.helper import getOtpValidator,otpValidator
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
        if not get_otp_validator:
            return Response(get_otp_validator)
        otp = 1234
        current_time = datetime.now()
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
                'message':'OTP send successfully'
              }
        return Response(res)

@api_view(['POST'])
def verify_otp(request):
    if request.method == 'POST':
        data = request.data
        otp_validator = otpValidator(data)
        if not otp_validator:
            return Response(otp_validator)
        try:
            otp_obj = OtpVerify.objects.get(country_code = data["country_code"],phone_no=data["phone_no"])
        except:
            res = {
                    'status':False,
                    'message':'something went wrong, please login again'
            }
            return Response(res)
        if data['otp'] != otp_obj.value:
            res = {
                    'status':False,
                    'message':'invalid otp'
            }
            return Response(res)
        
        res = {
                'status':True,
                'message':'OTP verified'
        }
        otp_obj.delete()
        return Response(res)
        
        