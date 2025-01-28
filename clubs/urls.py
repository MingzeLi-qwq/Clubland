from django.urls import path
from . import views

urlpatterns = [
    path('', views.club_list, name='club_list'),  # 社团列表
    path('<int:club_id>/create-news/', views.create_news, name='create_news'),  # 创建新闻
    path('<int:club_id>/create-event/', views.create_event, name='create_event'),  # 创建活动
    path('<int:club_id>/manage-members/', views.manage_members_view, name='manage_members'),

]
