import random
from django.core.management.base import BaseCommand
from faker import Faker
from forum_system.models import BlogPost

fake = Faker()

class Command(BaseCommand):
    help = "生成一些测试博客文章数据"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='生成博客文章的数量，默认为10篇'
        )

    def handle(self, *args, **options):
        count = options['count']
        created = 0
        for _ in range(count):
            title = fake.sentence(nb_words=6)
            content = '\n\n'.join(fake.paragraphs(nb=5))
            BlogPost.objects.create(title=title, content=content)
            created += 1
        self.stdout.write(self.style.SUCCESS(f"成功生成 {created} 篇博客文章"))