from django.core.management.base import BaseCommand
from club_system.models import Club

class Command(BaseCommand):

    def handle(self, *args, **options):
        print(list(Club.objects.all()))