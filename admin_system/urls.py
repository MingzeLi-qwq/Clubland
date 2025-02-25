# admin_system/urls.py
from django.urls import path
from . import views

urlpatterns = [
    #Admin Panel
    path('clubs/', views.AdminPanelClubs.as_view(), name='admin_panel_clubs'),
    path('users/', views.AdminPanelUsers.as_view(), name='admin_panel_users'),
    path('events/', views.AdminPanelEvents.as_view(), name='admin_panel_events'),
    path('requests/', views.AdminPanelRequests.as_view(), name='admin_panel_requests'),

    #Admin Panel Club
    path('clubs/general/int:<club_id>', views.AdminPanelClubsGeneral.as_view(), name='admin_panel_club_general'),
    path('clubs/members/int:<club_id>', views.AdminPanelClubsMembers.as_view(), name='admin_panel_club_members'),
    path('clubs/news/int:<club_id>', views.AdminPanelClubsNews.as_view(), name='admin_panel_club_news'),
    path('clubs/event/int:<club_id>', views.AdminPanelClubsEvents.as_view(), name='admin_panel_club_events'),
    #删除club
    path('clubs/general/delete/int:<club_id>', views.AdminDeleteClub.as_view(), name='admin_delete_club'),


    #Admin Panel User
    path('user/information/<str:username>/', views.AdminPanelUserInformation.as_view(), name='admin_panel_user_information'),
    path('user/memberships/<str:username>/', views.AdminPanelUserMemberships.as_view(), name='admin_panel_user_memberships'),
    path('user/requests/<str:username>/', views.AdminPanelUserRequests.as_view(), name='admin_panel_user_requests'),

    #Admin Panel Request
    path('requests/new_club/', views.AdminPanelNewClubRequests.as_view(), name='admin_panel_new_club_requests'),
    path('requests/new_club/detail/<int:ncRequest_id>', views.AdminPanelNewClubRequestDetail.as_view(), name='admin_panel_new_club_requests_detail'),
]