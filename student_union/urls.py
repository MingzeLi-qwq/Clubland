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
from django.urls import path, include, re_path
import user_system.views
import club_system.views
import event_system.views
import club_hub.views
import message_system.views
from user_system.views import home
from user_system.views import change_password
from notification_system.views import notification_list
from notification_system.views import notification_detail
from notification_system.views import mark_all_as_read
from message_system.views import get_messages, send_message, search_users
from notification_system.views import delete_notification
from notification_system.views import delete_all_notifications
from club_hub.views import ImageUploadView
from club_hub.views import ManagerCheckView


import event_system.views
import news_system.views
import forum_system.views

from django.conf import settings
from django.conf.urls.static import static

import admin_system.views

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
    path('about-us/', user_system.views.about_us, name='about_us'),
    path('login/', user_system.views.LogInView.as_view(), name='login'),
    path('logout/', user_system.views.LogOutView, name='logout'),
    path('change_password/', user_system.views.change_password, name='change_password'), 
    path('mine/', user_system.views.Mine, name='Mine'),

    # Personal Dashboard / 个人资料页
    path('dashboard/personal_information/', user_system.views.DashboardPersonalInformation.as_view(), name='dashboard_personal_information'),
    path('dashboard/my_club/', user_system.views.DashboardMyClub.as_view(), name='dashboard_my_club'),
    path('dashboard/my_requests', user_system.views.DashboardMyRequests.as_view(), name='dashboard_my_requests'),
    path('dashboard/requests/new_club/', user_system.views.NewClubRequestsView.as_view(), name='dashboard_new_club_requests'),
    # 个人资料页下的membership details
    path('dashboard/my_club/detail/<int:club_id>/', user_system.views.ClubMembershipDetail.as_view(), name='dashboard_my_club_detail'),


    # path('societies/', user_system.views.societies, name='societies'),

    # Notification related / 通知相关页面
    path('notifications/', notification_list, name='notifications'),
    path('notifications/<int:notification_id>/', notification_detail, name='notification_detail'),
    path('notifications/mark_all_as_read/', mark_all_as_read, name='mark_all_as_read'),

    path('notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('notifications/delete-all/', delete_all_notifications, name='delete_all_notifications'),
          


    # Summernote related / 富文本编辑器相关
    path('summernote/', include('django_summernote.urls')),

    # News related / 新闻相关页面
    path('news/', include('news_system.urls', namespace='news_system')),

    # Forum related / 论坛相关页面
    path('forum/', include('forum_system.urls', namespace='forum_system')),


    path('api/', include('club_hub.urls')),
    path("club-view/<int:club_id>/", club_hub.views.club_hub_view, name="club_hub_view"),

    # Message related / 消息相关
    path('messages/message_dashboard', message_system.views.message_dashboard, name='message_dashboard'),
    path('api/messages/', message_system.views.get_messages, name='get_messages'),
    path('api/send/', message_system.views.send_message, name='send_message'),
    path("api/search_users/", message_system.views.search_users, name="search_users"),
    #---------------------------------------------------- Event related / Event相关页面 -----------------------------------------------------------------------
    path('events/', include('event_system.urls')),
    #-------------------------------------------------------- Event related END ----------------------------------------------------------------------------


    #---------------------------------------------------- Club related / Club相关页面 -----------------------------------------------------------------------
    path('clubs/', include('club_system.urls')),
    #-------------------------------------------------------- Club related END ----------------------------------------------------------------------------


    #---------------------------------------------------- Admin related / Admin相关页面 -----------------------------------------------------------------------
    path('admin_panel/', include('admin_system.urls')),
    #-------------------------------------------------------- Admin related END ------------------------------------------------------------------------------

    #--------------------------------------- Password verification for dangerous operations / 危险操作的密码验证 --------------------------------------------------
    path('verify-admin-password/', admin_system.views.verifyAdminPassword, name='verify_admin_password'),
    #--------------------------------------------Password verification for dangerous operations END --------------------------------------------------------

    path("api/", include("club_hub.urls")),
    path("api/upload-image/", ImageUploadView.as_view(), name="upload-image"),
    path('api/clubs/<int:club_id>/is_manager/', ManagerCheckView.as_view(), name='check-manager'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)