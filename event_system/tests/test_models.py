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
        # Prepare test data
        self.user = UserModel.objects.create_user(
            username='testuser',
            password='testpass123',
            account_type=User.ACCOUNT_TYPE_USER
        )

        # Depending on whether your Club model uses string or integer primary keys:
        # If using a string primary key:
        #   club = Club.objects.create(club_id='club_1', name='Test Club')
        # If using an integer primary key (default AutoField), use this:
        self.club = Club.objects.create(
            name='Test Club'
        )

        self.category1 = Category.objects.create(name='Music')
        self.category2 = Category.objects.create(name='Sports')

        # Create an Event
        self.event = Event.objects.create(
            name='Test Event',
            club=self.club,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2),
            location='Room 101',
            description='This is a test event'
        )
        self.event.categories.add(self.category1)  # Add a category to the event

        # Add an RSVP for the regular user
        self.rsvp = RSVP.objects.create(
            user=self.user,
            event=self.event,
            status=True
        )

    def test_category_creation(self):
        """
        Test creation of Category model and its __str__ representation
        """
        self.assertTrue(Category.objects.filter(name='Music').exists())
        self.assertTrue(Category.objects.filter(name='Sports').exists())

        cat = Category.objects.get(name='Music')
        self.assertEqual(str(cat), 'Music')  

    def test_event_creation(self):
        """
        Test creation of Event model, ForeignKey to Club, and ManyToMany with Category
        """
        self.assertTrue(Event.objects.filter(name='Test Event').exists())
        event_obj = Event.objects.get(name='Test Event')

        # Check ForeignKey to Club
        self.assertEqual(event_obj.club, self.club)
        # Check associated categories
        self.assertIn(self.category1, event_obj.categories.all())
        self.assertNotIn(self.category2, event_obj.categories.all()) 
        self.assertEqual(str(event_obj), f"Test Event by {self.club.name}")

    def test_event_participants_relation(self):
        """
        Test the ManyToMany relation of Event with participants
        (Should be empty unless manually added)
        """
        self.assertFalse(self.user in self.event.participants.all())

        # Manually add participant
        self.event.participants.add(self.user)
        self.assertTrue(self.user in self.event.participants.all())

    def test_rsvp_creation(self):
        """
        Test RSVP model creation and __str__ (if implemented)
        """
        self.assertTrue(RSVP.objects.filter(user=self.user, event=self.event).exists())
        rsvp_obj = RSVP.objects.get(user=self.user, event=self.event)
        self.assertTrue(rsvp_obj.status)
        self.assertIsNotNone(rsvp_obj.timestamp)

    def test_rsvp_unique_constraint(self):
        """
        Test unique_together = ('user', 'event')
        Creating duplicate RSVP should raise IntegrityError
        """
        with self.assertRaises(IntegrityError):
            RSVP.objects.create(
                user=self.user,
                event=self.event,
                status=False
            )

    def test_event_str_representation(self):
        """
        Test string representation of Event
        """
        event_obj = Event.objects.get(name='Test Event')
        self.assertEqual(str(event_obj), f"Test Event by {self.club.name}")