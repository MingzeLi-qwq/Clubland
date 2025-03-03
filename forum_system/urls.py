










]    path('thread_post/<int:pk>/delete/', ThreadPostDeleteView.as_view(), name='threadpost_delete'),    # 修改 URL 名称为 threadpost_delete    path('post/<int:pk>/delete/', BlogPostDeleteView.as_view(), name='blog_delete'),    path('post/new/', BlogPostCreateView.as_view(), name='blog_create'),    path('post/<int:pk>/', BlogPostDetailView.as_view(), name='blog_detail'),    path('', BlogPostListView.as_view(), name='blog_list'),urlpatterns = [from .views import BlogPostListView, BlogPostDetailView, BlogPostCreateView, BlogPostDeleteView, ThreadPostDeleteViewfrom django.urls import pathfrom django.urls import path
from student_union import settings
from .views import (
    BlogPostListView, BlogPostDetailView, BlogPostCreateView,
    BlogPostDeleteView, ThreadPostDeleteView)
app_name = 'forum_system'

urlpatterns = [
    path('', BlogPostListView.as_view(), name='blog_list'),
    path('post/<int:pk>/', BlogPostDetailView.as_view(), name='blog_detail'),
    path('post/new/', BlogPostCreateView.as_view(), name='blog_create'),
    path('post/<int:pk>/delete/', BlogPostDeleteView.as_view(), name='blog_delete'),
    path('thread_post/<int:pk>/delete/', ThreadPostDeleteView.as_view(), name='comment_delete'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)