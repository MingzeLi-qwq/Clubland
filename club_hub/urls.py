from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WidgetViewSet, get_csrf_token  # 新增get_csrf_token导入

router = DefaultRouter()
router.register(r'clubs/(?P<club_id>\d+)/widgets', WidgetViewSet, basename="widgets")

urlpatterns = [
    path("", include(router.urls)),
    path("csrf/", get_csrf_token, name="get-csrf"),  # 添加CSRF端点
]
