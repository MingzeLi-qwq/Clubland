from django.test import TestCase
from club_system.models import Club
from user_system.models import User
from event_system.models import Category, Event, RSVP
from datetime import datetime
from django.utils import timezone
from django.db import IntegrityError


class CategoryModelTest(TestCase):
    def test_category_str(self):
        category = Category.objects.create(name="Sports")
        self.assertEqual(str(category), "Sports")


class EventModelTest(TestCase):
    def setUp(self):
        # 创建依赖对象：Club 与 User（假设它们至少包含 name 或 username 字段）
        self.club = Club.objects.create(name="Test Club")
        self.user = User.objects.create(username="testuser")
        
        # 转换为 timezone-aware datetime
        start_time = timezone.make_aware(datetime(2023, 1, 1, 10, 0, 0))
        end_time = timezone.make_aware(datetime(2023, 1, 1, 12, 0, 0))
        
        # 创建 Event 实例
        self.event = Event.objects.create(
            name="Test Event",
            club=self.club,
            start_time=start_time,
            end_time=end_time,
            location="Test Location",
            description="This is a test event.",
        )
        # 创建 Category 并关联到 Event
        self.category = Category.objects.create(name="Sports")
        self.event.categories.add(self.category)
        
        # 添加参与者
        self.event.participants.add(self.user)
    
    def test_event_str(self):
        expected_str = f"{self.event.name} by {self.club.name}"
        self.assertEqual(str(self.event), expected_str)
    
    def test_event_categories(self):
        self.assertIn(self.category, self.event.categories.all())
    
    def test_event_participants(self):
        self.assertIn(self.user, self.event.participants.all())


class RSVPModelTest(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name="Test Club")
        self.user = User.objects.create(username="testuser")
        start_time = timezone.make_aware(datetime(2023, 1, 1, 10, 0, 0))
        end_time = timezone.make_aware(datetime(2023, 1, 1, 12, 0, 0))
        self.event = Event.objects.create(
            name="Test Event RSVP",
            club=self.club,
            start_time=start_time,
            end_time=end_time,
            location="Test Location",
            description="This is a test event for RSVP.",
        )
    
    def test_rsvp_creation(self):
        rsvp = RSVP.objects.create(user=self.user, event=self.event, status=True)
        self.assertIsNotNone(rsvp.id)
        self.assertTrue(rsvp.status)
    
    def test_rsvp_unique_together(self):
        # 第一次创建 RSVP
        RSVP.objects.create(user=self.user, event=self.event, status=True)
        # 重复创建相同 user 与 event 的记录应违反 unique_together 约束，抛出 IntegrityError
        with self.assertRaises(IntegrityError):
            RSVP.objects.create(user=self.user, event=self.event, status=False)

