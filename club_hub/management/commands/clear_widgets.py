from django.core.management.base import BaseCommand
from club_hub.models import Widget

class Command(BaseCommand):
    help = 'Clear all component data'

    def handle(self, *args, **options):
        count = Widget.objects.all().count()
        Widget.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} components'))