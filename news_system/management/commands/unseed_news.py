from django.core.management.base import BaseCommand
from news_system.models import News

class Command(BaseCommand):
    help = "删除所有测试新闻数据"

    def handle(self, *args, **kwargs):
        deleted_count, _ = News.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"成功删除 {deleted_count} 篇新闻"))
