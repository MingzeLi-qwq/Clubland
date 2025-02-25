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
    help = '为每个社团创建10个随机活动 / Create 10 random events for each club'

    def handle(self, *args, **options):
        self.create_categories()
        self.create_events_for_each_club()
        
    def create_categories(self):
        """创建分类数据（如果不存在）"""
        for name in event_categories:
            Category.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("✅ 成功创建/验证分类数据"))

    def create_events_for_each_club(self):
        """为每个社团创建活动数据"""
        clubs = Club.objects.all()
        users = User.objects.all()
        categories = Category.objects.all()

        if not users.exists():
            self.stdout.write(self.style.ERROR("❌ 错误：没有可用用户，请先创建用户"))
            return
        if not clubs.exists():
            self.stdout.write(self.style.ERROR("❌ 错误：没有可用社团，请先创建社团"))
            return

        for club in clubs:
            for i in range(10):  # 每个社团创建 10 个活动
                event_name = f"{club.name} - {self.generate_event_name()}"

                # 生成时间范围（从过去7天到未来30天）
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 6))

                event = Event.objects.create(
                    name=event_name,
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description=fake.paragraph(nb_sentences=8),
                )

                # 添加随机分类（1-3个）
                event.categories.set(random.sample(list(categories), k=random.randint(1, 3)))

                self.stdout.write(f"🎉 创建活动：{event.name}  属于社团 {club.name}")

        self.stdout.write(self.style.SUCCESS(f"✅ 成功为 {clubs.count()} 个社团创建活动，每个社团 10 个活动"))

    def generate_event_name(self):
        """生成符合真实场景的活动标题"""
        prefixes = ["崩坏学园3", "崩坏：星穹铁道", "未定事件铺", "元神", "大别野"]
        types = [
            "学妹认识", "学姐鉴赏", "宅男电竞", "猛男健身", "多人交流",
            "单人运动", "多人交配", "多人玩耍", "多人运动"
        ]
        return f"{random.choice(prefixes)} {fake.word().capitalize()} {random.choice(types)}"
