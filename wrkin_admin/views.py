from wrkin_admin.models import *
from wrkin_admin.helper import loginValidator
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
from custom_jwt import generateJwtToken,verifyJwtToken


# Create your views here.


@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        data = request.data
        login_validator = loginValidator(data)
        if not login_validator['status']:
            return Response(login_validator)
        try:
            user = AdminUser.objects.get(email = data['email'])
        except:
            res = {
                    'status':False,
                    'message':'email does not exist'
                  }
            return Response(res)
        if not check_password(data['password'],user.password):
            res = {
                    'status':False,
                    'message':'invalid credentials'
                  }
            return Response(res)
        generate_jwt_token = generateJwtToken(user.id)
        if generate_jwt_token['status']:
            user.token = generate_jwt_token['token']
            user.save()
            res = {
                    'status':True,
                    'message':'login successful',
                    'token':generate_jwt_token['token']
                }
            return Response(res)


@api_view(['GET'])
def index(request):
    new_pass = make_password('12345678')
    AdminUser.objects.update(password = new_pass)

    obj = AdminUser.objects.values()
    return Response(obj)

