from wrkin_customer.models import CustomerUser,OtpVerify,Rooms
from datetime import datetime

def getOtpValidator(data):
    try:
        country_code = data['country_code']
    except:
        res = {
                'status':False,
                'mesage':'country_code is required'
                }
        return res
    # if not isinstance(country_code,(int)):
    #     res = {
    #             'status':False,
    #             'message':'please provide a valid country_code'
    #             }
    #     return res
    try:
        phone_no = data['phone_no']
    except:
        res = {
                'status':False,
                'mesage':'phone_no is required'
                }
        return res
    # if not isinstance(phone_no,(int)):
    #     res = {
    #             'status':False,
    #             'message':'please provide a valid phone_no'
    #             }
    #     return res
    try:
        CustomerUser.objects.get(country_code = country_code,phone_no=phone_no)
    except:
        res = {
                'status':False,
                'message':'phone_no not registered, please talk to admin'
            }
        return res
    res = {
            'status':True
          }
    return res

def otpValidator(data):
    try:
        otp = data['otp']
    except:
        res = {
                'status':False,
                'message':'otp is required'
        }
        return res
    if not isinstance(otp,(int)):
        res = {
                'status':False,
                'message':'please provide a valid otp'
              }
        return res
    try:
        otp_id = data['otp_id']
    except:
        res = {
                'status':False,
                'mesage':'otp_id is required'
                }
        return res
    if not isinstance(otp_id,(int)):
        res = {
                'status':False,
                'message':'please provide a valid otp_id'
                }
        return res
    try:
        OtpVerify.objects.get(id = otp_id)
    except:
        res = {
                'status':False,
                'message':'otp invalid otp_id'
            }
        return res
    
    res = {
            'status':True
          }
    return res


def retryOtpValidator(data):
    try:
        otp_id = data['otp_id']
    except:
        res = {
                'status':False,
                'message':'otp_id is required'
            }
        return res
    res = {
            'status':True
         }
    return res   


def createTaskvalidator(data):
    title = data.get('title',False)
    description = data.get('description',False)
    from_user = data.get('from',False)
    to_user = data.get('to',False)
    start_date = data.get('start_date',False)
    end_date = data.get('end_date',False)
    priority = data.get('priority',False)

    if not title:
        res = {
                'status':False,
                'message':'title is required'
            }
        return res
    if not description:
        res = {
                'status':False,
                'message':'description is required'
            }
        return res
    if not from_user:
        res = {
                'status':False,
                'message':'from is required'
            }
        return res
    try:
        CustomerUser.objects.get(id = from_user)
    except:
        res = {
                'status':False,
                'message':'invalid from user id'
            }
        return res
    if not to_user:
        res = {
                'status':False,
                'message':'to is required'
            }
        return res
    try:
        CustomerUser.objects.get(id = to_user)
    except:
        res = {
                'status':False,
                'message':'invalid to user id'
            }
        return res
    if not start_date:
        res = {
                'status':False,
                'message':'start_date is required'
            }
        return res
    try:
        datetime.strptime(start_date,"%Y-%m-%d")
    except:
        res = {
                'status':False,
                'message':'invalid start_date format'
            }
        return res
    if not end_date:
        res = {
                'status':False,
                'message':'end_date is required'
            }
        return res
    try:
        datetime.strptime(end_date,"%Y-%m-%d")
    except:
        res = {
                'status':False,
                'message':'invalid end_date format'
            }
        return res
    if not priority:
        res = {
                'status':False,
                'message':'priority is required'
            }
        return res
    if priority not in ['high','low','medium']:
        res = {
                'status':False,
                'message':'invalid value for priority'
            }
        return res
    res = {
            'status':True,
            'title':title,
            'description':description,
            'from_user':int(from_user),
            'to_user':int(to_user),
            'start_date':start_date,
            'end_date':end_date,
            'priority':priority
    }
    return res
    
def getRoomId(user_list):
    try:
        room_obj = Rooms.objects.get(users__contains = user_list,is_group = False)
    except:      
        room_obj = Rooms(
                            users = [int(user_list[0]),int(user_list[1])],
                            is_enabled = True,
                            is_group = False,
                        )
        room_obj.save()
    return room_obj.id

def groupCreateVaidator(data):
    try:
        group_members = data['group_members']
    except:
        res = {
                'status':False,
                'message':'group_members is required'
        } 
        return res
    if not isinstance(group_members,(list)):
        res = {
                'status':False,
                'message':'group_members must be array'
        }
        return res
    if not all(isinstance(x, int) for x in group_members):
        res = {
                'status':False,
                'message':'group_members must be array of integers'
        }
        return res
    try:
        group_name = data['group_name']
        group_name = group_name.strip()
    except:
        res = {
                'status':False,
                'message':'group_name is required'
        }
        return res
    if len(group_name) < 1:
        res = {
                'status':False,
                'message':'group_name must have atleast one character'
        }
        return res
    for i in group_members:
        try:
            CustomerUser.objects.get(id = i)
        except:
            res = {
                    'status':False,
                    'message':'invalid user_id',
                    'user_id':i
            }
            return res
    res = {
            'status':True
    }
    return res
    