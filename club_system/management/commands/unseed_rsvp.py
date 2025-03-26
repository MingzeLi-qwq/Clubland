from django.core.management.base import BaseCommand
from event_system.models import RSVP

class Command(BaseCommand):
    """Django Management Command to unseed RSVP data from the database."""
    
    help = "Removes all RSVP data from the database"

    def handle(self, *args, **options):
        """Delete all RSVP records from the database."""
        self.stdout.write("deleteing RSVPs...")
        deleted_count, _ = RSVP.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted_count} RSVPs have been deleted."))
