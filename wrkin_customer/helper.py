from wrkin_customer.models import CustomerUser,OtpVerify

def getOtpValidator(data):
    try:
        country_code = data['country_code']
    except:
        res = {
                'status':False,
                'mesage':'country_code is required'
                }
        return res
    if not isinstance(country_code,(int)):
        res = {
                'status':False,
                'message':'please provide a valid country_code'
                }
        return res
    try:
        phone_no = data['phone_no']
    except:
        res = {
                'status':False,
                'mesage':'phone_no is required'
                }
        return res
    if not isinstance(phone_no,(int)):
        res = {
                'status':False,
                'message':'please provide a valid phone_no'
                }
        return res
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
        country_code = data['country_code']
    except:
        res = {
                'status':False,
                'mesage':'country_code is required'
                }
        return res
    if not isinstance(country_code,(int)):
        res = {
                'status':False,
                'message':'please provide a valid country_code'
                }
        return res
    try:
        phone_no = data['phone_no']
    except:
        res = {
                'status':False,
                'mesage':'phone_no is required'
                }
        return res
    if not isinstance(phone_no,(int)):
        res = {
                'status':False,
                'message':'please provide a valid phone_no'
                }
        return res
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