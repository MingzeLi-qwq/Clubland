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
from django.urls import path,include
import user_system.views
import club_system.views
from user_system.views import home

app_name = 'accounts'

urlpatterns = [
    # Main pages
    path('admin/', admin.site.urls),
    #path('accounts/', include('accounts.urls')),
    path('', user_system.views.home, name='home'),
    path('signup/', user_system.views.SignUpView.as_view(), name='signup'),

    path('login/', user_system.views.LogInView.as_view(), name='login'),
    path('logout/', user_system.views.LogOutView, name='logout'),
    
    path('dashboard/', user_system.views.DashboardView.as_view(), name='dashboard'),
    # path('societies/', user_system.views.societies, name='societies'),
    path('news/', user_system.views.news, name='news'),
    path('events/', user_system.views.events, name='events'),


    # Club related / Club相关页面
    path('clubs/', club_system.views.clubs, name='clubs'),
    path('clubs/detail/<int:club_id>/', club_system.views.ClubDetailView.as_view(), name='club_detail'),
    path('clubs/detail/register_membership/<int:club_id>/', club_system.views.RegisterMembershipView.as_view(), name='register_membership'),
    path('clubs/detail/cancel_membership/<int:club_id>/', club_system.views.CancelMembershipView.as_view(), name='cancel_membership'),

    # Club Dashboard
    path('clubs/dashboard/general', club_system.views.ClubDashboardGeneral.as_view(), name='club_dashboard_general'),
    path('clubs/dashboard/members', club_system.views.ClubDashboardMembers.as_view(), name='club_dashboard_members'),
    path('clubs/dashboard/news', club_system.views.ClubDashboardNews.as_view(), name='club_dashboard_news'),
    path('clubs/dashboard/events', club_system.views.ClubDashboardEvents.as_view(), name='club_dashboard_events'),

]