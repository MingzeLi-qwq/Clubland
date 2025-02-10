from django.urls import path
from .views import BlogPostListView, BlogPostDetailView, BlogPostCreateView

app_name = 'forum_system'

urlpatterns = [
    path('', BlogPostListView.as_view(), name='blog_list'),
    path('post/<int:pk>/', BlogPostDetailView.as_view(), name='blog_detail'),
    path('post/new/', BlogPostCreateView.as_view(), name='blog_create'),
]
