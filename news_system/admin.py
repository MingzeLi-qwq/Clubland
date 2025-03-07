# news_system/admin.py
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import News, Comment

@admin.register(News)
class NewsAdmin(SummernoteModelAdmin):  # 继承 SummernoteModelAdmin
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at',)
    summernote_fields = ('content',)  # 只将 content 字段应用富文本编辑器

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('news', 'author', 'created_at')
    search_fields = ('content',)
    list_filter = ('created_at',)