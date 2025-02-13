from django.core.management.base import BaseCommand
from event_system.models import Event, Category

class Command(BaseCommand):
    help = "删除所有活动和活动分类 / Remove all events and event categories"

    def handle(self, *args, **kwargs):
        # 删除所有活动
        event_count = Event.objects.count()
        Event.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"成功删除 {event_count} 个活动"))

        # 删除所有分类
        category_count = Category.objects.count()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"成功删除 {category_count} 个活动分类"))

