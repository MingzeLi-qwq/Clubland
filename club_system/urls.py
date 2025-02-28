# club_system/urls.py
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.clubs, name='clubs'),
    path('detail/<int:club_id>/', views.ClubDetailView.as_view(), name='club_detail'),
    path('detail/register_membership/<int:club_id>/', views.RegisterMembershipView.as_view(), name='register_membership'),
    path('detail/cancel_membership/<int:club_id>/', views.CancelMembershipView.as_view(), name='cancel_membership'),

    # Club Manager
    path('manager/general/<int:club_id>/', views.ClubManagerGeneral.as_view(), name='club_manager_general'),
    path('manager/members/<int:club_id>/', views.ClubManagerMembers.as_view(), name='club_manager_members'),
    path('manager/news/<int:club_id>/', views.ClubManagerNews.as_view(), name='club_manager_news'),
    path('manager/events/<int:club_id>/', views.ClubManagerEvents.as_view(), name='club_manager_events'),

    # Club manager change name and description
    path('manager/update_name/<int:club_id>/', views.UpdateClubName.as_view(), name='update_club_name'),
    path('manager/update_description/<int:club_id>/', views.UpdateClubDescription.as_view(), name='update_club_description'),

    # Club manager remove manager
    path('manager/remove_manager/<int:club_id>/<str:username>/', views.RemoveManagerView.as_view(), name='remove_manager'),
    path('manager/set_manager/<int:club_id>/<str:username>/', views.SetManagerView.as_view(), name='set_manager'),

    # js搜索用户
    path('manager/search_users/', views.SearchUsersView.as_view(), name='search_users'),

    # 添加与删除member
    path('manager/add_member/<int:club_id>/<str:username>/', views.AddMemberView.as_view(), name='add_member'),
    path('manager/remove_member/<int:club_id>/<str:username>/', views.RemoveMemberView.as_view(), name='remove_member'),

    # 创建新的Club
    path('apply-new-club/', views.ApplyNewClubView.as_view(), name='apply_new_club'),

    # event 
    path("manager/event/general/<int:club_id>/<int:event_id>", views.ClubManagerEventGeneral.as_view(), name="club_manager_event_general"),
    path("manager/event/RSVPs/<int:club_id>/<int:event_id>", views.ClubManagerEventRSVPs.as_view(), name="club_manager_event_RSVPs"),
]