from django.urls import path
from . import views
from .views import user_center_view
from django.http import HttpResponse

def placeholder_view(request):
    return HttpResponse("This is the users module placeholder.")

# 定义路由
urlpatterns = [
    path('', placeholder_view, name='users_home'),
        path('user-center/', user_center_view, name='user_center'),
        path('club-requests/', views.club_requests_view, name='club_requests'),
        path('my-clubs/', views.my_clubs_view, name='my_clubs'),


]
