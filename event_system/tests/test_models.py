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
        Testing Category Model Creation and __str__ Expression
        """
        self.assertTrue(Category.objects.filter(name='Music').exists())
        self.assertTrue(Category.objects.filter(name='Sports').exists())

        cat = Category.objects.get(name='Music')
        self.assertEqual(str(cat), 'Music')  

    def test_event_creation(self):
        """
        Test Event Model Creation, Foreign Key Club, ManyToMany Category
        """
        self.assertTrue(Event.objects.filter(name='Test Event').exists())
        event_obj = Event.objects.get(name='Test Event')

        self.assertEqual(event_obj.club, self.club)
        self.assertIn(self.category1, event_obj.categories.all())
        self.assertNotIn(self.category2, event_obj.categories.all())  
        self.assertEqual(str(event_obj), f"Test Event by {self.club.name}")

    def test_event_participants_relation(self):
        """
        Test Event's ManyToMany participants participants
        (empty by default unless you add them manually)
        """
        self.assertFalse(self.user in self.event.participants.all())

    
        self.event.participants.add(self.user)
        self.assertTrue(self.user in self.event.participants.all())

    def test_rsvp_creation(self):
        """
        Test RSVP model creation and __str__ 
        """
        self.assertTrue(RSVP.objects.filter(user=self.user, event=self.event).exists())
        rsvp_obj = RSVP.objects.get(user=self.user, event=self.event)
        self.assertTrue(rsvp_obj.status)
        self.assertIsNotNone(rsvp_obj.timestamp)

    def test_rsvp_unique_constraint(self):
        """
        Test unique_together = ('user', 'event')
        Inserting the same user/event again should throw IntegrityError
        """
        with self.assertRaises(IntegrityError):
            RSVP.objects.create(
                user=self.user,
                event=self.event,
                status=False
            )

    def test_event_str_representation(self):
        """
        Testing Event String Performance
        """
        event_obj = Event.objects.get(name='Test Event')
        self.assertEqual(str(event_obj), f"Test Event by {self.club.name}")
