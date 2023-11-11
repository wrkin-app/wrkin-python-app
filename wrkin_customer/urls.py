from django.urls import path
from wrkin_customer.views import *
urlpatterns = [
                path('get_otp',get_otp,name='get_otp'),
                path('verify_otp',verify_otp,name='verify_otp'),
                path('retry_otp',retry_otp,name='retry_otp'),
                path('user_name_update',user_name_update,name='user_name_update'),
                path('my_team',my_team,name='my_team'),
                path('my_chats',my_chats,name='my_chats'),
                path('my_room_chat',my_room_chat,name='my_room_chat'),
                path('my_room_chat_reversed',my_room_chat_reversed,name='my_room_chat_reversed'),
                path('get_user_list',get_user_list,name='get_user_list'),
                path('start_chat',start_chat,name='start_chat'),
                path('create_task',create_task,name='create_task'),
                path('get_single_task',get_single_task,name='get_single_task'),
                
                path('test_login',test_login,name='test_login'),
                path('test_chat_list',test_chat_list,name='test_chat_list'),
                path('demo',demo,name='demo'),
                
                
                
]