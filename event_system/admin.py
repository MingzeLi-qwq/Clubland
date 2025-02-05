from django.contrib import admin
from .models import Event  # 导入 Event 模型

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'club', 'start_time', 'location')  # 列表展示的字段
    search_fields = ('name', 'location')  # 可搜索字段
    filter_horizontal = ('participants',)  # 让多对多字段在 admin 界面更方便管理
