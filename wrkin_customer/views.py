from wrkin_customer.models import *
from wrkin_customer.helper import getOtpValidator,otpValidator,retryOtpValidator,createTaskvalidator,getRoomId,groupCreateVaidator,getGroupValidator
from wrkin_customer.decorators import authRequired
from custom_jwt import generateJwtToken,verifyJwtToken
from wrkin_customer.serializers import ChatSerializer
from wrkin_customer.messanger import otp_sender
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
from datetime import datetime,date
from time import sleep
import pytz
import random

# Create your views here.


@api_view(['POST'])
def get_otp(request):
    if request.method == 'POST':
        data = request.data
        get_otp_validator = getOtpValidator(data)
        if not get_otp_validator['status']:
            return Response(get_otp_validator)
        current_time = datetime.now()
        try:
            otp_obj = OtpVerify.objects.get(country_code = data['country_code'],phone_no = data['phone_no'])
            prev_otp_time = current_time - otp_obj.created_at
            prev_otp_time = prev_otp_time.total_seconds()//60
            if prev_otp_time < 30:
                if otp_obj.try_count < 3:
                    # otp = 1234
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
            otp = random.randint(1000, 9999)
            otp_obj = OtpVerify(
                                    country_code = data['country_code'],
                                    phone_no = data['phone_no'],
                                    value = otp,
                                    try_count = 1,
                                    created_at = current_time,
                            )
            otp_sender_res = otp_sender(otp, data['phone_no'])
            print(otp_sender_res,type(otp_sender_res))
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
                    'initial_login': initial_login_flag
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
@api_view(['GET'])
def logout(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        cust_obj = CustomerUser.objects.get(id = user_id)
        cust_obj.secure_token = ''
        cust_obj.save()
        res = {
                'status':True,
                'message':'user logged out'
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
        chats = Chats.objects.filter(room_id = room_id)\
                             .annotate(name = F('user__name'))\
                             .values('id','user_id','name','message','created_at','is_task','task_id','task__title','task__description','task__from_user_id','task__to_user_id','task__start_date','task__end_date','task__priority').order_by('-id')
        print(chats)
        chat_serialized = ChatSerializer(chats,many=True)
        paginator = Paginator(chat_serialized.data, 30)
        if int(page_no) > paginator.num_pages:
            page = []
        else:
            page = list(paginator.get_page(page_no))

        print(page)

        res = {
                'status':True,
                'message':'',
                'chat':page
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
                                users = user_list,
                                is_enabled = True,
                                is_group = False,
                                created_at = datetime.now()
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


@authRequired
@api_view(['GET'])
def get_assigned_task_list(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        task_obj = Task.objects.filter(to_user_id = user_id,start_date__lte = date.today())

        pending = task_obj.filter(status = 'pending',end_date__gte = date.today()).count()
        overdue = task_obj.filter(status = 'pending',end_date__lt = date.today()).count()
        completed = task_obj.filter(status = 'completed').count()
        task_list = task_obj.annotate(
                                        current_status=Case(
                                                                When(status='pending', end_date__lt=date.today(), then=Value('overdue')),
                                                                default=F('status'),
                                                                output_field=models.CharField(),  # Adjust the field type if necessary
                                                                ),
                                        assignee_name = F('from_user__name')
                                    )\
        .values('id','title','current_status','end_date','assignee_name').order_by('-id')

        res = {
                'status':True,
                'message':'',
                'pending':pending,
                'overdue':overdue,
                'completed':completed,
                'task_list':task_list
        }
        return Response(res)
    

@authRequired
@api_view(['GET'])
def get_created_task_list(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        task_obj = Task.objects.filter(from_user_id = user_id)
        pending = task_obj.filter(status = 'pending',end_date__gte = date.today()).count()
        overdue = task_obj.filter(status = 'pending',end_date__lt = date.today()).count()
        completed = task_obj.filter(status = 'completed').count()
        task_list = task_obj.annotate(
                                        current_status=Case(
                                                                When(status='pending', end_date__lt=date.today(), then=Value('overdue')),
                                                                default=F('status'),
                                                                output_field=models.CharField(),  # Adjust the field type if necessary
                                                                ),
                                        assigned_to = F('to_user__name')
                                    )\
        .values('id','title','current_status','end_date','assigned_to').order_by('-id')

        res = {
                'status':True,
                'message':'',
                'pending':pending,
                'overdue':overdue,
                'completed':completed,
                'task_list':task_list
        }
        return Response(res)
    

@authRequired
@api_view(['POST'])
def admin_add_people(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'POST':
        user_id = request.META.get('HTTP_USER_ID')
        try:
            user_obj = CustomerUser.objects.get(id = user_id)
            org_id = user_obj.company_profile_id
        except:
            res = {
                'status':False,
                'message':'invalid user'
                }
            return Response(res)
        if not user_obj.is_admin:
            res = {
                    'status':False,
                    'message':'permission not available'
            }
            return Response(res)
        people_list = request.data
        for i in people_list:
            try:
                i['name']
                i['country_code']
                i['phone_number']
            except:
                res = {
                    'status':False,
                    'message':'invalid structure of body'
                }
                return Response(res)
        new_added = []
        already_existed = []
        for i in people_list:
            try:
                CustomerUser.objects.get(country_code = i['country_code'],phone_no = i['phone_number'])
                already_existed.append(i)
            except:

                cust_obj = CustomerUser(
                                            name = i['name'],
                                            country_code = i['country_code'],
                                            phone_no = i['phone_number'],
                                            company_profile_id = org_id,
                                            is_admin = False,
                                        )
                cust_obj.save()
                new_added.append(i)

        res = {
                'status':True,
                'message':'contacts added to orgainzation',
                'new_added':new_added,
                'already_existed':already_existed

        }
        return Response(res)
    
@authRequired
@api_view(['POST'])
def create_group(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'POST':
        user_id = request.META.get('HTTP_USER_ID')
        data = request.data
        group_create_validator =  groupCreateVaidator(data)
        if not group_create_validator['status']:
            return Response(group_create_validator)
        group_members = data['group_members']
        group_members.append(int(user_id))
        group_members = sorted(list(set(group_members)))
        group_name = data['group_name']
        room_obj = Rooms(
                                users = group_members,
                                group_name = group_name,
                                admin_id = user_id,
                                is_enabled = True,
                                is_group = True,
                                created_at = datetime.now()
                            )
        room_obj.save()
        res = {
                'status':True,
                'message':'group created',
                'room_id':8
                # 'room_id':room_obj.id
        }
        return Response(res)
    
@authRequired
@api_view(['GET'])
def my_groups(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        user_id = request.META.get('HTTP_USER_ID')
        groups = Rooms.objects.filter(users__contains = [user_id],is_group = True).values_list('id',flat=True).values('id','group_name','created_at')
        for i in groups:
            try:
                chat_obj = Chats.objects.filter(room_id = i['id']).order_by('-created_by')
                if chat_obj.count() < 1:
                    raise Exception
                i['last_message'] = chat_obj.first()['message']
                i['last_message_date'] = chat_obj.first()['created_at']
            except:
                i['last_message'] = ''
                i['last_message_date'] = i['created_at']
        groups = sorted(groups, key=lambda x: x['last_message_date'], reverse=True)
        res = {
                'status':True,
                'message':'',
                'groups':groups
        }
        return Response(res)
    
@authRequired
@api_view(['GET'])
def get_group_details(request,**kwargs):
    auth_status = kwargs.get('auth_status')
    if not auth_status:
        res = {
                'status':False,
                'message':'authetication failed'
        }
        return Response(res)
    if request.method == 'GET':
        data = request.data
        get_group_validator = getGroupValidator(data)
        if not get_group_validator['status']:
            return Response(get_group_validator)
        group_id = data['group_id']
        group_obj = Rooms.objects.get(id = group_id)
        group_name = group_obj.group_name
        group_members_ids = group_obj.users
        group_admin = group_obj.admin_id
        group_members = CustomerUser.objects.filter(id__in = group_members_ids).values('id','name','image').order_by('name')

        res = {
                "group_name":group_name,
                "group_admin":group_admin,
                "group_members":group_members
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