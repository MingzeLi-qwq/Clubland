from django.urls import path

from django.http import HttpResponse

def placeholder_view(request):
    return HttpResponse("This is the users module placeholder.")

# 定义路由
urlpatterns = [
    path('', placeholder_view, name='users_home'),
]
