from functools import wraps
from custom_jwt import verifyJwtToken
from wrkin_customer.models import CustomerUser

# Define a custom decorator function
def authRequired(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_status = False
        secure_token = request.META.get('HTTP_SECURE_TOKEN')
        user_id = request.META.get('HTTP_USER_ID')
        if not secure_token:
            return view_func(request, *args, **kwargs,auth_status=auth_status)
        if not user_id:
            return view_func(request, *args, **kwargs,auth_status=auth_status)
        try:
            CustomerUser.objects.get(id = user_id,secure_token=secure_token)
        except:
            return view_func(request, *args, **kwargs,auth_status=auth_status)
        verify_jwt_token = verifyJwtToken(secure_token)
        if not verify_jwt_token['status']:
            return view_func(request, *args, **kwargs,auth_status=auth_status)
        try:
            user_id = int(user_id)
        except:
            return view_func(request, *args, **kwargs,auth_status=auth_status)
        if verify_jwt_token['data']['user_id'] == user_id:
            auth_status = True
        return view_func(request, *args, **kwargs,auth_status=auth_status,user_id=user_id)
    
    return wrapper