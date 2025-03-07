from django.core.management.base import BaseCommand
from event_system.models import Event, Category

class Command(BaseCommand):
    help = "Remove all events and event categories"

    def handle(self, *args, **kwargs):
        # Remove all events
        event_count = Event.objects.count()
        Event.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {event_count} events"))

        # Remove all categories
        category_count = Category.objects.count()
        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {category_count} categories"))

