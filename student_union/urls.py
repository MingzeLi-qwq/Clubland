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
from django.urls import path,include, re_path
import user_system.views
import club_system.views
import event_system.views
import club_hub.views
from user_system.views import home
from user_system.views import change_password
from notification_system.views import notification_list

import event_system.views
import forum_system.views
from forum_system.views import ckeditor_image_upload

from rest_framework.routers import DefaultRouter
from club_hub.views import WidgetViewSet

app_name = 'accounts'
router = DefaultRouter()
router.register(r'clubs/(?P<club_id>\d+)/widgets', WidgetViewSet, basename="widgets")

urlpatterns = [
    # Main pages
    path('admin/', admin.site.urls),
    #path('accounts/', include('accounts.urls')),
    path('', user_system.views.home, name='home'),
    path('signup/', user_system.views.SignUpView.as_view(), name='signup'),

    path('login/', user_system.views.LogInView.as_view(), name='login'),
    path('logout/', user_system.views.LogOutView, name='logout'),
    path('change-password/', user_system.views.change_password, name='change_password'), 

    # Personal Dashboard / 个人资料页
    path('dashboard/personal_information', user_system.views.DashboardPersonalInformation.as_view(), name='dashboard_personal_information'),
    path('dashboard/my_club', user_system.views.DashboardMyClub.as_view(), name='dashboard_my_club'),
    path('dashboard/my_requests', user_system.views.DashboardMyRequests.as_view(), name='dashboard_my_requests'),
    path('dashboard/requests/new_club/', user_system.views.NewClubRequestsView.as_view(), name='dashboard_new_club_requests'),
    # 个人资料页下的membership details
    path('dashboard/my_club/detail/<int:club_id>/', user_system.views.ClubMembershipDetail.as_view(), name='dashboard_my_club_detail'),


    # path('societies/', user_system.views.societies, name='societies'),
    path('news/', user_system.views.news, name='news'),

    #Notification related / 通知相关页面
    path('notifications/', notification_list, name='notifications'),

    # Events related / Events相关页面
    path('events/home/', event_system.views.events_home, name='events_home'),
    path('events/', event_system.views.EventListView.as_view(), name='events'),
    path('events/<int:pk>/', event_system.views.event_detail, name='event_detail'),
    path('events/<int:pk>/rsvp/', event_system.views.rsvp_toggle, name='rsvp_toggle'),
  

    #---------------------------------------------------- Club related / Club相关页面 -----------------------------------------------------------------------
    path('clubs/', club_system.views.clubs, name='clubs'),
    path('clubs/detail/<int:club_id>/', club_system.views.ClubDetailView.as_view(), name='club_detail'),
    path('clubs/detail/register_membership/<int:club_id>/', club_system.views.RegisterMembershipView.as_view(), name='register_membership'),
    path('clubs/detail/cancel_membership/<int:club_id>/', club_system.views.CancelMembershipView.as_view(), name='cancel_membership'),

    # Club Manager
    path('clubs/manager/general/<int:club_id>/', club_system.views.ClubManagerGeneral.as_view(), name='club_manager_general'),
    path('clubs/manager/members/<int:club_id>/', club_system.views.ClubManagerMembers.as_view(), name='club_manager_members'),
    path('clubs/manager/news/<int:club_id>/', club_system.views.ClubManagerNews.as_view(), name='club_manager_news'),

    # Club manager change name and description
    path('clubs/manager/update_name/<int:club_id>/', club_system.views.UpdateClubName.as_view(), name='update_club_name'),
    path('clubs/manager/update_description/<int:club_id>/', club_system.views.UpdateClubDescription.as_view(), name='update_club_description'),

    # Club manager remove manager
    path('clubs/manager/remove_manager/<int:club_id>/<str:username>/', club_system.views.RemoveManagerView.as_view(), name='remove_manager'),
    path('clubs/manager/set_manager/<int:club_id>/<str:username>/', club_system.views.SetManagerView.as_view(), name='set_manager'),

    # js搜索用户
    path('clubs/manager/search_users/', club_system.views.SearchUsersView.as_view(), name='search_users'),

    # 添加与删除member
    path('clubs/manager/add_member/<int:club_id>/<str:username>/', club_system.views.AddMemberView.as_view(), name='add_member'),
    path('clubs/manager/remove_member/<int:club_id>/<str:username>/', club_system.views.RemoveMemberView.as_view(), name='remove_member'),

    # Events
    path('clubs/manager/events/<int:club_id>/', club_system.views.ClubManagerEvents.as_view(), name='club_manager_events'),
    path("clubs/manager/events/<int:event_id>/rsvps/", club_system.views.EventRSVPListView.as_view(), name="event_rsvps"),
    re_path(r"^clubs/manager/events/(?P<event_id>\d+)/remove_rsvp/(?P<username>[\w.@+-]+)/$", club_system.views.RemoveRSVPView.as_view(), name="remove_rsvp"),
    re_path(r"^clubs/manager/events/(?P<event_id>\d+)/add_rsvp/(?P<username>[\w.@+-]+)/$", club_system.views.AddRSVPView.as_view(), name="add_rsvp"),

    # 创建新的Club
    path('clubs/apply-new-club/', club_system.views.ApplyNewClubView.as_view(), name='apply_new_club'),
    #-------------------------------------------------------- Club related END ----------------------------------------------------------------------------

    # Forum related / 论坛相关页面
        path('ckeditor/', include('ckeditor_uploader.urls')),  # 富文本编辑器图片上传
        path('ckeditor/upload/', ckeditor_image_upload, name='ckeditor_upload'),
        path('forum/', include('forum_system.urls', namespace='forum_system')),


    path('api/', include('club_hub.urls')),
    path("club-dashboard/<int:club_id>/", club_hub.views.club_dashboard, name="club_dashboard"),
]   

