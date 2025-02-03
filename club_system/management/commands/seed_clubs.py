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
    help = 'Seeds the clubs database with 10 default data, and assign members for them. / 为俱乐部数据库提供10个默认数据, 并为它们分配成员'

    def create_clubs(self):
        created_count = 0
        self.created_clubs = []
        for name in club_names:
            description = fake.sentence(nb_words=30)  # 生成 30 个单词的描述
            '''The get_or_create() function returns two values, one for the object being created, and a boolean indicating whether the creation was successful or not.'''
            '''get_or_create()函数会返回两个值, 一个是被创建的对象, 和一个布尔值代表创建是否成功'''
            club, created = Club.objects.get_or_create(name=name, defaults={'description': description})
            if created:
                created_count += 1
                self.created_clubs.append(club)

        self.stdout.write(self.style.SUCCESS(f"Successfully creat {created_count} clubs / 成功创建{created_count}个club"))

    

    def handle(self, *args, **kwargs):
        self.create_clubs() 
