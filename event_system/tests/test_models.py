from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError

from django.contrib.auth import get_user_model
from club_system.models import Club
from user_system.models import User
from ..models import Category, Event, RSVP

UserModel = get_user_model()

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username='testuser',
            password='testpass123',
            account_type=User.ACCOUNT_TYPE_USER
        )
        self.club = Club.objects.create(
            name='Test Club'
        )

        self.category1 = Category.objects.create(name='Music')
        self.category2 = Category.objects.create(name='Sports')

        self.event = Event.objects.create(
            name='Test Event',
            club=self.club,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2),
            location='Room 101',
            description='This is a test event'
        )
        self.event.categories.add(self.category1) 

        self.rsvp = RSVP.objects.create(
            user=self.user,
            event=self.event,
            status=True
        )

    def test_category_creation(self):
        """
        测试 Category 模型的创建和 __str__ 表达
        """
        self.assertTrue(Category.objects.filter(name='Music').exists())
        self.assertTrue(Category.objects.filter(name='Sports').exists())

        cat = Category.objects.get(name='Music')
        self.assertEqual(str(cat), 'Music')  # 测试 __str__

    def test_event_creation(self):
        """
        测试 Event 模型的创建, 外键Club, ManyToMany Category
        """
        self.assertTrue(Event.objects.filter(name='Test Event').exists())
        event_obj = Event.objects.get(name='Test Event')

        # 检查外键Club
        self.assertEqual(event_obj.club, self.club)
        # 检查关联的分类
        self.assertIn(self.category1, event_obj.categories.all())
        self.assertNotIn(self.category2, event_obj.categories.all())
        self.assertEqual(str(event_obj), f"Test Event by {self.club.name}")

    def test_event_participants_relation(self):
        """
        测试 Event 的 ManyToMany 参加者 participants
        """
        self.assertFalse(self.user in self.event.participants.all())

        # 手动加一下
        self.event.participants.add(self.user)
        self.assertTrue(self.user in self.event.participants.all())

    def test_rsvp_creation(self):
        """
        测试 RSVP 模型的创建
        """
        self.assertTrue(RSVP.objects.filter(user=self.user, event=self.event).exists())
        rsvp_obj = RSVP.objects.get(user=self.user, event=self.event)
        self.assertTrue(rsvp_obj.status)
        self.assertIsNotNone(rsvp_obj.timestamp)

    def test_rsvp_unique_constraint(self):
        """
        测试 unique_together = ('user', 'event')
        再插入同一 user/event 应抛 IntegrityError
        """
        with self.assertRaises(IntegrityError):
            RSVP.objects.create(
                user=self.user,
                event=self.event,
                status=False
            )

    def test_event_str_representation(self):
        """
        测试Event字符串表现
        """
        event_obj = Event.objects.get(name='Test Event')
        self.assertEqual(str(event_obj), f"Test Event by {self.club.name}")
