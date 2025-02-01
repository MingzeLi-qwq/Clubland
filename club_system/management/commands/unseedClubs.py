from django.core.management.base import BaseCommand
from club_system.models import Club

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'uneeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        Club.objects.all().delete()