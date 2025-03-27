from django.core.management.base import BaseCommand
from news_system.models import News

class Command(BaseCommand):
    help = "Delete all test news data"

    def handle(self, *args, **kwargs):
        deleted_count, _ = News.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} news articles."))
