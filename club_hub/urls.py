from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WidgetViewSet

router = DefaultRouter()
router.register(r'clubs/(?P<club_id>\d+)/widgets', WidgetViewSet, basename="widgets")

urlpatterns = [
    path("", include(router.urls)),
]
