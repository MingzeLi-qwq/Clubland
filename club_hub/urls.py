from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WidgetViewSet, get_csrf_token
from .views import ClubBackgroundUpdateView, ClubInfoView

router = DefaultRouter()
router.register(r'clubs/(?P<club_id>\d+)/widgets', WidgetViewSet, basename="widgets")

urlpatterns = [
    path("", include(router.urls)),
    path("csrf/", get_csrf_token, name="get-csrf"),
    path("clubs/<int:club_id>/background/", ClubBackgroundUpdateView.as_view(), name="update-club-background"),
    path("clubs/<int:club_id>/info/", ClubInfoView.as_view(), name="club-info"),

]
