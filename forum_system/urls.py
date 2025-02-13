from django.urls import path
from .views import (
    BlogPostListView, BlogPostDetailView, BlogPostCreateView,
    BlogPostDeleteView, CommentDeleteView, ckeditor_image_upload  # 导入新创建的视图
)

app_name = 'forum_system'

urlpatterns = [
    path('', BlogPostListView.as_view(), name='blog_list'),
    path('post/<int:pk>/', BlogPostDetailView.as_view(), name='blog_detail'),
    path('post/new/', BlogPostCreateView.as_view(), name='blog_create'),
    path('post/<int:pk>/delete/', BlogPostDeleteView.as_view(), name='blog_delete'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('ckeditor/upload/', ckeditor_image_upload, name='ckeditor_upload'),
]
