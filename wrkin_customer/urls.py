from django.urls import path
from wrkin_customer.views import *
urlpatterns = [
                path('index',index),
                path('get_otp',get_otp),
                path('verify_otp',verify_otp),
                path('retry_otp',retry_otp),
]