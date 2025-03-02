from django.urls import path
from student_union import settings
from .views import (
    NewsListView, NewsDetailView, NewsCreateView,
    NewsDeleteView, CommentDeleteView, load_events
)
app_name = 'news_system'

urlpatterns = [
    path('', NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('news/new/', NewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('ajax/load-events/', load_events, name='ajax_load_events'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)