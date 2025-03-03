from django.urls import path
from .views import (
    BlogPostListView, 
    BlogPostDetailView, 
    BlogPostCreateView,
    BlogPostDeleteView, 
    ThreadPostDeleteView
)

app_name = 'forum_system'

urlpatterns = [
    path('', BlogPostListView.as_view(), name='blog_list'),
    path('post/<int:pk>/', BlogPostDetailView.as_view(), name='blog_detail'),
    path('post/new/', BlogPostCreateView.as_view(), name='blog_create'),
    path('post/<int:pk>/delete/', BlogPostDeleteView.as_view(), name='blog_delete'),
    path('thread_post/<int:pk>/delete/', ThreadPostDeleteView.as_view(), name='threadpost_delete'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)