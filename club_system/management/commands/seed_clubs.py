import random
from django.core.management.base import BaseCommand
from club_system.models import Club, Membership
from user_system.models import User
from faker import Faker

fake = Faker()

club_names = [
    "AI Club", "Photography Club", "Music Club", "Chess Club", "Drama Club",
    "Sports Club", "Coding Club", "Astronomy Club", "Gaming Club", "Book Club"
]


class Command(BaseCommand):
    help = 'Seeds the clubs database with 10 default data, and assign members for them.'

    def create_clubs(self):
        created_count = 0
        self.created_clubs = []
        for name in club_names:
            description = fake.sentence(nb_words=30)
            '''The get_or_create() function returns two values, one for the object being created, and a boolean indicating whether the creation was successful or not.'''
            club, created = Club.objects.get_or_create(name=name, defaults={'description': description})
            if created:
                created_count += 1
                self.created_clubs.append(club)

        self.stdout.write(self.style.SUCCESS(f"Successfully creat {created_count} clubs"))

    

    def handle(self, *args, **kwargs):
        self.create_clubs() 
