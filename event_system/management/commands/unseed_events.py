# events/management/commands/unseed_events.py
from django.core.management.base import BaseCommand
from event_system.models import Event, Category

# 与 seed_events.py 中完全相同的预定义分类
EVENT_CATEGORIES = [
    "Workshop", "Sports", "Social", "Tech", "Arts",
    "Academic", "Music", "Outdoor", "Career", "Cultural"
]

class Command(BaseCommand):
    help = '删除所有由 seed_events 创建的活动及分类数据'

    def handle(self, *args, **options):
        # 删除所有活动
        event_count = Event.objects.count()
        Event.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"✅ 成功删除 {event_count} 个活动数据"))

        # 删除预定义分类（只删除 seed 创建的）
        categories = Category.objects.filter(name__in=EVENT_CATEGORIES)
        category_count = categories.count()
        categories.delete()
        self.stdout.write(self.style.SUCCESS(f"✅ 成功删除 {category_count} 个分类数据"))