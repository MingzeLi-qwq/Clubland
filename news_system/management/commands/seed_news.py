import random
from django.core.management.base import BaseCommand
from faker import Faker
from news_system.models import News

fake = Faker()

class Command(BaseCommand):
    help = "Generate some test news data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of news generated, default is 10'
        )

    def handle(self, *args, **options):
        count = options['count']
        created = 0
        for _ in range(count):
            title = fake.sentence(nb_words=6)
            content = '\n\n'.join(fake.paragraphs(nb=5))
            News.objects.create(title=title, content=content)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {created} news article"))
