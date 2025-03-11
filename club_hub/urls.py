from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import WidgetViewSet

app_name = 'club_hub'

router = DefaultRouter()
router.register(r'clubs/(?P<club_id>\d+)/widgets', WidgetViewSet, basename="widgets")

urlpatterns = [
    path("", include(router.urls)),
    path("csrf/", views.get_csrf_token, name="get-csrf"),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]
