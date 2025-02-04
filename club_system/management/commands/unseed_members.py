from django.core.management.base import BaseCommand
from club_system.models import Membership

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'uneeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        Membership.objects.all().delete()
