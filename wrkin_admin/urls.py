from django.urls import path
from wrkin_admin.views import *
urlpatterns = [
                path('login',login,name='login'),
                path('index',index,name='index'),
]