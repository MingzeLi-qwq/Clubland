# events/management/commands/seed_events.py
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from club_system.models import Club
from faker import Faker
from user_system.models import User
from event_system.models import Event, Category

fake = Faker()

# 预定义活动分类
event_categories = [
    "Workshop", "Sports", "Social", "Tech", "Arts",
    "Academic", "Music", "Outdoor", "Career", "Cultural"
]

# 预定义活动地点关键词
locations = [
    "Main Hall", "Room 302", "Sports Complex", "Campus Lawn",
    "Auditorium", "Online", "Conference Room", "Student Center"
]

class Command(BaseCommand):
    help = '创建10个随机活动数据并关联分类 / Create 10 random events with categories'

    def handle(self, *args, **options):
        self.create_categories()
        self.create_events()
        
    def create_categories(self):
        """创建分类数据（如果不存在）"""
        for name in event_categories:
            Category.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("成功创建/验证分类数据"))

    def create_events(self):
        """创建活动数据"""
        # 获取所有用户和分类
        clubs = Club.objects.all()

        users = User.objects.all()
        
        categories = Category.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.ERROR("错误：没有可用用户，请先创建用户"))
            return
        if not clubs.exists():
            self.stdout.write(self.style.ERROR("错误：没有可用社团，请先创建社团"))
            return

        for i in range(10):  # 创建10个活动
            club = random.choice(clubs)
              
            event_name = f"{club.name} - {self.generate_event_name()}"

            # 生成时间范围（未来30天内）
            start_time = timezone.now() + timedelta(days=random.randint(1,30))
            end_time = start_time + timedelta(hours=random.randint(2,6))

            
            
            event = Event.objects.create(
                name=event_name, 
                club = Club.objects.order_by('?').first(),
    
                start_time=start_time,
                end_time=end_time,
                location=f"{random.choice(locations)} - {fake.street_address()}",
                description=fake.paragraph(nb_sentences=8),
                is_featured=random.choice([True, False, False])  # 1/3概率精选
            )
            
            # 添加随机分类（1-3个）
            event.categories.set(random.sample(list(categories), k=random.randint(1,3)))
            
            self.stdout.write(f"创建活动：{event.name}")

        self.stdout.write(self.style.SUCCESS("成功创建10个活动数据"))

    def generate_event_name(self):
        """生成符合真实场景的活动标题"""
        prefixes = ["年度", "新生", "春季", "冬季", "周末"]
        types = [
            "工作坊", "训练营", "之夜", "比赛", "交流会",
            "分享会", "研讨会", "体验课", "马拉松"
        ]
        return f"{random.choice(prefixes)}{fake.word().capitalize()} {random.choice(types)}"


