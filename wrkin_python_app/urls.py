from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/admin/',include('wrkin_admin.urls')),
    path('api/v1/user/',include('wrkin_customer.urls')),
]
