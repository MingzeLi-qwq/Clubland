from django.core.management.base import BaseCommand
from forum_system.models import BlogPost

class Command(BaseCommand):
    help = "删除所有测试博客文章数据"

    def handle(self, *args, **kwargs):
        deleted_count, _ = BlogPost.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"成功删除 {deleted_count} 篇博客文章"))
