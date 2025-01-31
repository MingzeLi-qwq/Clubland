from django.core.management.base import BaseCommand
from club_system.models import Clubs

class Command(BaseCommand):

    def handle(self, *args, **options):
        print(list(Clubs.objects.all()))