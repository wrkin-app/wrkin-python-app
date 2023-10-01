from django.contrib import admin
from django.urls import path,include

from wrkin_admin.urls import urlpatterns as admin_urls
from wrkin_customer.urls import urlpatterns as customer_urls

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def main_urls(request):
    if request.method == 'GET':
        res = {}
        routes = []
        admin_route = 'api/v1/admin/'
        for i in admin_urls:
            if i != 'None':
                routes.append(f'{admin_route}{i.name}')
        res['admin_route'] = routes
        routes = []
        customer_route = 'api/v1/user/'
        for i in customer_urls:
            if i != 'None':
                routes.append(f'{customer_route}{i.name}')
        res['customer_route'] = routes
        return Response(res)


urlpatterns = [
    path('',main_urls),
    path('admin/', admin.site.urls),
    path('api/v1/admin/',include('wrkin_admin.urls')),
    path('api/v1/user/',include('wrkin_customer.urls')),
]
