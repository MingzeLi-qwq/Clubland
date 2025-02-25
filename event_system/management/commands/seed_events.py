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
        
        start_time = timezone.now() + timedelta(days=random.randint(5, 30)),

        for club in clubs:
            if club.name == "AI Club":
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 6))
                event1 = Event.objects.create(
                    name="AI Hackathon",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="All club members interested in Artificial Intelligence are welcome to participate in the AI Club Hackathon! In this 24-hour programming challenge, teams will collaborate to solve real-world AI problems, using techniques such as machine learning, computer vision, or natural language processing to develop innovative solutions. Whether you're a novice or an experienced developer, this is a great opportunity to learn and practice. The winning team will receive prizes and have the opportunity to present their project to industry experts!",
                )
                tech_category, created = Category.objects.get_or_create(name="Tech")
                event1.categories.add(tech_category)
                tech_category, created = Category.objects.get_or_create(name="Workshop")
                event1.categories.add(tech_category)
                self.stdout.write(f"Create Event:{event1.name}  For Club: {club.name}")

                
                start_time = timezone.now() + timedelta(days=random.randint(5, 30))
                end_time = start_time + timedelta(hours=random.randint(2, 6))
                event2 = Event.objects.create(
                    name="AI Ethics & Future Panel Discussion",
                    club=club,
                    start_time=start_time,
                    end_time=end_time,
                    location=f"{random.choice(locations)} - {fake.street_address()}",
                    description="What will the future of Artificial Intelligence look like?Will AI replace human jobs? How should we deal with the ethical issues brought by AI development? This symposium invites researchers in the field of AI, representatives of enterprises and experts in ethics to discuss the trend of AI development, social impact and potential risks. All community members are welcome to actively participate, put forward their questions and opinions, and have in-depth exchanges with the guests!"
                )
                tech_category, created = Category.objects.get_or_create(name="Tech")
                event2.categories.add(tech_category)
                self.stdout.write(f"Create Event:{event2.name}  For Club: {club.name}")

