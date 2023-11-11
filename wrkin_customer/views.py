from wrkin_customer.models import *
from wrkin_customer.helper import getOtpValidator,otpValidator,retryOtpValidator,createTaskvalidator,getRoomId
from wrkin_customer.decorators import authRequired
from custom_jwt import generateJwtToken,verifyJwtToken
from wrkin_customer.serializers import ChatSerializer
#-----------------------query related-------------------------------------------------
from django.db.models import Avg,Count,Case, When,Sum,BooleanField,DateTimeField,IntegerField,CharField
from django.db.models import F,Func,Q,Value, ExpressionWrapper, fields,OuterRef,Subquery
from django.db.models.functions import Now,Extract,Cast,TruncDate
from django.contrib.auth.hashers import make_password,check_password
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
#----------------------------restAPI--------------------------------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
#---------------------------python----------------------------------------------------
import jwt
from datetime import datetime
import pytz

# Create your views here.


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
                    'user_name':cust_obj.name,
                    'org_id':cust_obj.company_profile_id,
                    'is_admin':cust_obj.is_admin,
                    'initial_login': True
            }
            otp_obj.delete()
        else:
            res = {
                    'status':False,
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
@api_view(['PATCH'])
def user_name_update(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'PATCH':
        user_id = request.META.get('HTTP_USER_ID')
        name = request.GET.get('name')
        try:
            cust_obj = CustomerUser.objects.get(id = int(user_id))
        except:
            res = {
                    'status':False,
                    'message':'invalid user_id'
                  }
            return Response(res)
        if not name:
            res = {
                    'status':False,
                    'message':'name is required'
            }
            return Response(res)
        cust_obj.name = name
        cust_obj.save()
        res = {
                'status':True,
                'message':'name updated successfully'
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
        rooms = Rooms.objects.filter(users__contains = [user_id],is_group = False).values_list('id',flat=True)

        subquery = Chats.objects.filter(
                                            room_id=OuterRef('room_id')
                                        ).order_by('-id').values('id')[:1]
        chats = Chats.objects.filter(room_id__in = rooms).annotate(
                                                                   max_id=Subquery(subquery),
                                                                   last_message = F('message'),
                                                                   last_message_time = F('created_at'),
                                                                #    is_group = F('room__is_group'),
                                                                #    group_name = F('room__group_name'),
                                                                   chat_name = F('room__users')
                                                                   )\
                                                        .filter(
                                                                    id=F('max_id')
                                                                )\
                                                         .order_by('-created_at')\
                                                         .values('id','room_id','chat_name','last_message','last_message_time')
        for i in chats:
            for j in i['chat_name']:
                if j != int(user_id):
                    cust_obj = CustomerUser.objects.filter(id = j).values_list('image','name').last()
                    i['profile_image'] = cust_obj[0]
                    i['chat_name'] = cust_obj[1].split()[0]
                    i['user_id'] = j
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
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        room_id = request.GET.get('room_id')
        page_no = request.GET.get('page_no')
        if not room_id:
            res = {
                    'status':False,
                    'message':'room_id is required'
            }
            return Response(res)
        if not page_no:
            res = {
                    'status':False,
                    'message':'page_no is required'
            }
            return Response(res)
        chats = Chats.objects.filter(room_id = room_id).values('id','user_id','message','created_at','is_task','task_id','task__title','task__description','task__from_user_id','task__to_user_id','task__start_date','task__end_date','task__priority').order_by('id')
        chat_serialized = ChatSerializer(chats,many=True)
        paginator = Paginator(chat_serialized.data, 30)
        page = list(paginator.get_page(page_no))

        res = {
                'status':True,
                'message':'',
                'chat':page,
            }
        return Response(res)
    

@authRequired
@api_view(['GET'])
def my_room_chat_reversed(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        room_id = request.GET.get('room_id')
        page_no = request.GET.get('page_no')
        if not room_id:
            res = {
                    'status':False,
                    'message':'room_id is required'
            }
            return Response(res)
        if not page_no:
            res = {
                    'status':False,
                    'message':'page_no is required'
            }
            return Response(res)
        chats = Chats.objects.filter(room_id = room_id).values('id','user_id','message','created_at').order_by('-id')
        paginator = Paginator(chats, 30)
        page = list(paginator.get_page(page_no))
        res = {
                'status':True,
                'message':'',
                'chat':page,
            }
        return Response(res)

@authRequired
@api_view(['GET'])
def get_user_list(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        org_id = request.GET.get('org_id')
        if not org_id:
            res = {
                    'status':False,
                    'message':'org_id is required'
                }
            return Response(res)
        try:
            org_obj = CompanyProfile.objects.get(id = int(org_id))
        except:
            res = {
                    'status':False,
                    'message':'invalid org_id'
            }
            return Response(res)
        user_list = CustomerUser.objects.filter(company_profile_id = org_id).exclude(id = user_id).values('id','name','phone_no').order_by('name')
        res = {
                'status':True,
                'message':'',
                'user_list':user_list
        }
        return Response(user_list)
        
    
@authRequired
@api_view(['POST'])
def start_chat(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'POST':
        user_id = request.META.get('HTTP_USER_ID')
        reciever_user_id = request.GET.get('reciever_user_id')
        if not reciever_user_id:
            res = {
                    'status':False,
                    'message':'reciever_user_id is required'
                }
            return Response(res)
        try:
            reciever_name = CustomerUser.objects.get(id = int(reciever_user_id)).name
        except:
            res = {
                    'status':False,
                    'message':'invalid reciever_user_id'
            }
            return Response(res)
        user_list = sorted([user_id,reciever_user_id])
        try:
            room_obj = Rooms.objects.get(users__contains = user_list,is_group = False)
        except:      
            room_obj = Rooms(
                                users = [int(user_id),int(reciever_user_id)],
                                is_enabled = True,
                                is_group = False,
                            )
            room_obj.save()
        res = {
                'status':True,
                'message':'',
                'room_id':room_obj.id,
                'chat_name':reciever_name.split()[0]
        }
        return Response(res)
    
@authRequired
@api_view(['POST'])
def create_task(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'POST':
        data = request.data
        create_task_validator = createTaskvalidator(data)
        if create_task_validator['status']:
            task_obj = Task(
                                title = create_task_validator['title'],
                                description = create_task_validator['description'],
                                from_user_id = create_task_validator['from_user'],
                                to_user_id = create_task_validator['to_user'],
                                start_date = create_task_validator['start_date'],
                                end_date = create_task_validator['end_date'],
                                priority = create_task_validator['priority'],
                                status = "pending"
            )
            task_obj.save()
            user_list = sorted([create_task_validator['from_user'],create_task_validator['to_user']])
            room_id = getRoomId(user_list)
            chat_obj = Chats(
                                room_id = room_id,
                                user_id = int(create_task_validator['from_user']),
                                is_enabled = True,
                                is_task = True,
                                task_id = task_obj.id,
                                created_at = datetime.now(),
            )
            chat_obj.save()
            res = {
                    'status':True,
                    'message':'task created successfully',
                    'task_id': task_obj.id
            }
            return Response(res)
        else:
            return Response(create_task_validator)

@authRequired
@api_view(['GET'])
def get_single_task(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        task_id = request.GET.get('task_id',False)
        if not task_id:
            res = {
                    'status':False,
                    'message':'task_id is required'
            }
            return Response(res)
        try:
            task_obj = Task.objects.filter(id = task_id)
            if task_obj.count() < 1:
                raise Exception
        except:
            res = {
                    'status':False,
                    'message':'invalid task_id'
            }
            return Response(res)
        task_obj = task_obj.annotate(from_name = F('from_user__name'),
                                     to_name = F('to_user__name')).values().last()
        res = { 
                'status':True,
                'message':'task data',
                'task':{
                        'title':task_obj['title'],
                        'description':task_obj['description'],
                        'from':task_obj['from_name'],
                        'to':task_obj['to_name'],
                        'start_date':task_obj['start_date'],
                        'end_date':task_obj['end_date'],
                        'priority':task_obj['priority'],
                        'status':task_obj['status']
                }
        }
        return Response(res)

@api_view(['POST'])
def test_login(request):
    status = {
                'status':True,
                'user_id':1,
                'user_name':'Amrit',
                'secure_token':'sjdjhsfjdgskfbdjkfgfjk',
    }
    return Response(status)

@api_view(['GET'])
def test_chat_list(request):
    obj = Rooms.objects.annotate(room_id=F('id')).values('room_id')
    return Response({'chats':obj})

@api_view(['GET'])
def demo(request):
    obj = CustomerUser.objects.values()
    return Response(obj)