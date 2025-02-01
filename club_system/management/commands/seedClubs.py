import random
from django.core.management.base import BaseCommand
from club_system.models import Club
from faker import Faker

fake = Faker()

# club_names = [
#     "AI Club", "Photography Club", "Music Club", "Chess Club", "Drama Club",
#     "Sports Club", "Coding Club", "Astronomy Club", "Gaming Club", "Book Club"
# ]

club_names = [
    "Photography Club", "Drama Club", "Basketball Club", 
    "Coding Club", "Astronomy Club", "Gaming Club", "Book Club"
]

def create_clubs(self):
    created_count = 0
    for name in club_names:
        description = fake.sentence(nb_words=30)  # 生成 30 个单词的描述
        created = Club.objects.create(name=name, description=description)
        if created:
            created_count += 1

    self.stdout.write(self.style.SUCCESS(f"Successfully creat {created_count} clubs"))


class Command(BaseCommand):
    help = 'Seeds the clubs database with 10 default data'

    def handle(self, *args, **kwargs):
        create_clubs(self)