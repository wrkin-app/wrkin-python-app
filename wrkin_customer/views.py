from wrkin_customer.models import *
from wrkin_customer.helper import getOtpValidator,otpValidator,retryOtpValidator
from wrkin_customer.decorators import authRequired
from custom_jwt import generateJwtToken,verifyJwtToken
#-----------------------query related-------------------------------------------------
from django.db.models import Avg,Count,Case, When,Sum,BooleanField,DateTimeField,IntegerField,CharField
from django.db.models import F,Func,Q,Value, ExpressionWrapper, fields,OuterRef,Subquery
from django.db.models.functions import Now,Extract,Cast,TruncDate
from django.contrib.auth.hashers import make_password,check_password
from django.conf import settings
from django.utils import timezone
#----------------------------restAPI--------------------------------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
#---------------------------python----------------------------------------------------
import jwt
from datetime import datetime
import pytz

# Create your views here.


@api_view(['GET'])
def index(request):
    # res = CustomerUser.objects.values()
    # return Response(res)
    obj = Test.objects.filter(tag__contains = [1]).values()
    return Response(obj)

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
        initial_login_flag = False
        generate_jwt_token = generateJwtToken(cust_obj.id)
        if generate_jwt_token['status']:
            if not cust_obj.last_login_at:
                initial_login_flag = True
            india_timezone = pytz.timezone('Asia/Kolkata')
            current_datetime = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(india_timezone)
            cust_obj.secure_token = generate_jwt_token['token']
            cust_obj.last_login_at = current_datetime
            cust_obj.save()
            res = {
                    'status':True,
                    'message':'OTP verified',
                    'token':generate_jwt_token['token'],
                    'user_id':cust_obj.id,
                    'org_id':cust_obj.company_profile_id,
                    'initial_login': initial_login_flag
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


@authRequired
@api_view(['GET'])
def my_team(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        user_id = kwargs.get('user_id')
        india_timezone = pytz.timezone('Asia/Kolkata')
        my_team = CustomerUser.objects.exclude(id = user_id).annotate(
                                                                        active_status = Case(
                                                                                                When(last_login_at__isnull=True,then=Value(False)),
                                                                                                default=Value(True),
                                                                                                output_field=BooleanField()
                                                                                            ),
                                                                        login_time = ExpressionWrapper(
                                                                                                    F('last_login_at') + timezone.timedelta(hours=5, minutes=30),
                                                                                                    output_field=DateTimeField()
                                                                                                ),
                                                                        current_time = ExpressionWrapper(
                                                                                                    Now() + timezone.timedelta(hours=5, minutes=30),
                                                                                                    output_field=DateTimeField()
                                                                                                ),
                                                                        total_hrs = ExpressionWrapper(
                                                                                                        Extract(F('current_time') - F('login_time'),'hour') + 
                                                                                                        Extract(F('current_time') - F('login_time'), 'minute') / 60,
                                                                                                        output_field=IntegerField()
                                                                                                    )
                                                                   ).values('id','name','image','active_status','total_hrs')


        res = {
                'status':True,
                'message':'',
                'my_team':my_team
        }
        return Response(res)
        
@authRequired
@api_view(['GET'])
def my_chats(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        print(user_id)
        rooms = Rooms.objects.filter(users__contains = [user_id],is_group = False).values_list('id',flat=True)

        subquery = Chats.objects.filter(
                                            room_id=OuterRef('room_id')
                                        ).order_by('-id').values('id')[:1]
        chats = Chats.objects.filter(room_id__in = rooms).annotate(room_name = ExpressionWrapper(Value('abc'),output_field=CharField()),
                                                                   max_id=Subquery(subquery),
                                                                   last_message = F('message'),
                                                                   last_message_time = F('created_at'),
                                                                #    is_group = F('room__is_group'),
                                                                #    group_name = F('room__group_name'),
                                                                   chat_name = F('room__chat_name')
                                                                   )\
                                                        .filter(
                                                                    id=F('max_id')
                                                                )\
                                                         .order_by('-created_at')\
                                                         .values('id','room_id','chat_name','last_message','last_message_time')
        for i in chats:
            for j in i['chat_name']:
                if j['id'] != user_id:
                    i['profile_image'] = CustomerUser.objects.filter(id = j['id']).values_list('image',flat=True).last()
                    i['chat_name'] = j['name']
                break
            if i['last_message_time'].date() == datetime.now().date():
                i['last_message_time'] = i['last_message_time'].strftime('%H:%M:%S')
            else:
                i['last_message_time'] = i['last_message_time'].strftime('%d/%m/%Y')
        res = {
                'status':True,
                'message':'',
                'chats':chats
        }
        return Response(res)

@authRequired
@api_view(['GET'])
def my_room_chat(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        print(res)
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        room_id = request.GET.get('room_id')
        if not room_id:
            res = {
                    'status':False,
                    'message':'room_id is required'
            }
            return Response(res)
        chat = Chats.objects.filter(room_id = room_id).values('id','user_id','message')
        res = {
                'status':True,
                'message':'',
                'chat':chat
            }
        return Response(res)
    
@api_view(['POST'])
def test_login(request):
    if request.method == 'POST':
        data = request.data
        phone_no = data['phone_no']
        try:
            user = CustomerUser.objects.get(phone_no = phone_no)
        except:
            res = {
                    'status':False,
                    'message':'Login failed'
            }
            return Response(res)
        res = {
                'status':True,
                'message':'Login Success',
                'user_id':user.id,
                'user_name':user.name,
                'secure_token':user.secure_token
        }
        return Response(res)
    
@api_view(['GET'])
def test_chat_list(request):
    user_id = request.GET.get('user_id')
    print(user_id)
    rooms = Rooms.objects.filter(users__contains = [user_id]).values_list('id',flat=True)

    subquery = Chats.objects.filter(
                                        room_id=OuterRef('room_id')
                                    ).order_by('-id').values('id')[:1]
    
    chats = Chats.objects.filter(room_id__in = rooms).annotate(room_name = ExpressionWrapper(Value('abc'),output_field=CharField()),
                                                                max_id=Subquery(subquery),
                                                                is_group = F('room__is_group'),
                                                                group_name = F('room__group_name'),
                                                                chat_name = F('room__chat_name')
                                                                )\
                                                    .filter(
                                                                id=F('max_id')
                                                            )\
                                                        .order_by('-created_at')\
                                                        .values('id','room_id','is_group','group_name','chat_name')
    res = {
            'status':True,
            'message':'',
            'chats':chats
    }
    print(res)
    return Response(res)