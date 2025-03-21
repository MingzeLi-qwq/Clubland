# event_system/urls.py
from django.urls import path, re_path
from . import views

urlpatterns = [
    # Events list and detail page
    path('home/', views.events_home, name='events_home'),
    path('', views.EventListView.as_view(), name='events'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/rsvp/', views.rsvp_toggle, name='rsvp_toggle'),

    # Event update URLs
    path("update_name/<int:club_id>/<int:event_id>/", views.UpdateEventName.as_view(), name="update_event_name"),
    path("update_description/<int:club_id>/<int:event_id>/", views.UpdateEventDescription.as_view(), name="update_event_description"),
    path("update_time/<int:club_id>/<int:event_id>/", views.UpdateEventTime.as_view(), name='update_event_time'),
    path("update_location/<int:club_id>/<int:event_id>/", views.UpdateEventLocation.as_view(), name='update_event_location'),
    path("update_category/<int:club_id>/<int:event_id>/", views.UpdateEventCategory.as_view(), name='update_event_category'),
    path('delete_category/<int:category_id>/', views.DeleteCategoryView.as_view(), name='delete_category'),

    # create event URL
    path("create/<int:club_id>", views.CreateEventView.as_view(), name='create_event'),
    path('delete/<int:club_id>/<int:event_id>/', views.DeleteEvent.as_view(), name='delete_event'),
    path('remove_rsvp/<int:club_id>/<int:event_id>/<int:rsvp_id>/', views.RemoveRSVPView.as_view(), name='remove_rsvp'),


]