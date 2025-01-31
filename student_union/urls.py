"""
URL configuration for student_union project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.contrib.auth import views as auth_views

from users.views import user_center_view
from clubs.models import Club


def home_view(request):
    # 获取所有社团信息
    clubs = Club.objects.all()
    return render(request, 'home.html', {'clubs': clubs})


# 路由配置
urlpatterns = [
    path('admin/', admin.site.urls),        # 管理后台路由
    path('users/', include('users.urls')),  # 用户管理相关路由
    path('clubs/', include('clubs.urls')),  # 社团管理相关路由
    path('', home_view, name='home'),       # 根路径路由
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('user-center/', user_center_view, name='user_center'),
]
