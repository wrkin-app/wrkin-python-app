from django.urls import path
from wrkin_customer.views import *
urlpatterns = [
                path('index',index),
                path('get_otp',get_otp),
                path('verify_otp',verify_otp),
                path('retry_otp',retry_otp),
                path('my_team',my_team),
                path('my_chats',my_chats),
                path('my_room_chat',my_room_chat),

                path('test_login',test_login),
                path('test_chat_list',test_chat_list)

]