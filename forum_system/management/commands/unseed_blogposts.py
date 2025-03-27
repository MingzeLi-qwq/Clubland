from django.core.management.base import BaseCommand
from forum_system.models import BlogPost

class Command(BaseCommand):
    help = "Delete all test blog post data"

    def handle(self, *args, **kwargs):
        deleted_count, _ = BlogPost.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} blog posts"))
