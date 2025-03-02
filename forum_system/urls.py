from django.urls import path
from student_union import settings
from .views import (
    BlogPostListView, BlogPostDetailView, BlogPostCreateView,
    BlogPostDeleteView, CommentDeleteView, load_events)  # 导入新增视图
app_name = 'forum_system'

urlpatterns = [
    path('', BlogPostListView.as_view(), name='blog_list'),
    path('post/<int:pk>/', BlogPostDetailView.as_view(), name='blog_detail'),
    path('post/new/', BlogPostCreateView.as_view(), name='blog_create'),
    path('post/<int:pk>/delete/', BlogPostDeleteView.as_view(), name='blog_delete'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    # 新增用于 AJAX 更新活动列表的 URL
    path('ajax/load-events/', load_events, name='ajax_load_events'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)