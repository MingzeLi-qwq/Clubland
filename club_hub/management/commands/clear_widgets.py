from django.core.management.base import BaseCommand
from club_hub.models import Widget

class Command(BaseCommand):
    help = '清空所有组件数据'

    def handle(self, *args, **options):
        count = Widget.objects.all().count()
        Widget.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'成功删除 {count} 个组件'))