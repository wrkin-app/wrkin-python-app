from django.urls import path
from wrkin_customer.views import *
urlpatterns = [
                path('index',index,name='index'),
                path('get_otp',get_otp,name='get_otp'),
                path('verify_otp',verify_otp,name='verify_otp'),
                path('retry_otp',retry_otp,name='retry_otp'),
                path('my_team',my_team,name='my_team'),
                path('my_chats',my_chats,name='my_chats'),
                path('my_room_chat',my_room_chat,name='my_room_chat'),

                path('test_login',test_login,name='test_login'),
                path('test_chat_list',test_chat_list,name='test_chat_list')

]