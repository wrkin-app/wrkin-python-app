from wrkin_admin.models import *
from wrkin_admin.helper import ROLES_CHOICES,loginValidator
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
        res = {
                'status':True,
                'message':'login successful',
                'token':user.token
              }
        return Response(res)

        return Response(res)


# def index(request):
#     password = "wrkinakansha"
#     output = make_password(password)
#     return HttpResponse(output)

