from django.contrib import admin
from .models import Club, News, Event, Membership

# 使用装饰器注册 Club 模型
@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'leader')

# 手动注册其他模型
admin.site.register(News)
admin.site.register(Event)
admin.site.register(Membership)
