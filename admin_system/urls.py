# admin_system/urls.py
from django.urls import path
from . import views
from event_system import views as event_views

urlpatterns = [
    #Admin Panel
    path('clubs/', views.AdminPanelClubs.as_view(), name='admin_panel_clubs'),
    path('users/', views.AdminPanelUsers.as_view(), name='admin_panel_users'),
    path('requests/', views.AdminPanelRequests.as_view(), name='admin_panel_requests'),

    #Admin Panel Club
    path('clubs/general/<int:club_id>', views.AdminPanelClubsGeneral.as_view(), name='admin_panel_club_general'),
    path('clubs/members/<int:club_id>', views.AdminPanelClubsMembers.as_view(), name='admin_panel_club_members'),
    path('clubs/news/<int:club_id>', views.AdminPanelClubsNews.as_view(), name='admin_panel_club_news'),
    path('clubs/events/<int:club_id>', views.AdminPanelClubsEvents.as_view(), name='admin_panel_club_events'),
    path('clubs/dashboard/<int:club_id>', views.AdminPanelClubsDashboard.as_view(), name='admin_panel_club_dashboard'),
    path('clubs/general/delete/<int:club_id>', views.AdminDeleteClub.as_view(), name='admin_delete_club'),
    #Admin Panel Club event
    path('clubs/event/general/<int:club_id>/<int:event_id>', views.AdminPanelClubsEventGeneral.as_view(), name='admin_panel_club_event_general'),
    path('clubs/event/RSVPs/<int:club_id>/<int:event_id>', views.AdminPanelClubsEventRSVPs.as_view(), name='admin_panel_club_event_RSVPs'),
    path('clubs/event/search_rsvp_candidates/', event_views.SearchRSVPCandidatesView.as_view(), name='search_rsvp_candidates'),
    path('clubs/event/add_rsvp/<int:club_id>/<int:event_id>/<str:username>/', event_views.AddRSVPView.as_view(), name='add_rsvp'),

#Admin Panel User
    path('user/information/<str:username>/', views.AdminPanelUserInformation.as_view(), name='admin_panel_user_information'),
    path('user/memberships/<str:username>/', views.AdminPanelUserMemberships.as_view(), name='admin_panel_user_memberships'),
    path('user/memberships/remove/<str:username>/<int:club_id>/', views.AdminPanelRemoveMemberships.as_view(), name='admin_panel_remove_memberships'),

    #Admin Panel Request
    path('requests/new_club/', views.AdminPanelNewClubRequests.as_view(), name='admin_panel_new_club_requests'),
    path('requests/new_club/detail/<int:ncRequest_id>', views.AdminPanelNewClubRequestDetail.as_view(), name='admin_panel_new_club_requests_detail'),
    path('requests/new_club/review/<int:request_id>/', views.AdminReviewNewClubRequest.as_view(), name='admin_review_new_club_request'),
]