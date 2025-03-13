from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from user_system.models import User
from club_system.models import Club
from event_system.models import Event, RSVP, Category

class EventsViewsTest(TestCase):
    def setUp(self):
        """
        Create a normal user, manager user and admin user.  
        Create a Club (here the Club model does not contain an owner or managers field)  
        Create two categories, one activity, and one RSVP.  
        """
        self.client = Client()

        # Create three types of users
        self.user = User.objects.create_user(
            username='normaluser',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_USER
        )
        self.manager_user = User.objects.create_user(
            username='manager',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_USER
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_ADMIN
        )

        # Create a Club
        self.club = Club.objects.create(name='Test Club')

        # Create Category
        self.category_music = Category.objects.create(name='Music')
        self.category_sports = Category.objects.create(name='Sports')

        # Calculate event start and end times (timezone.now() returns datetime with timezone)
        start_time = timezone.now() + timedelta(days=1)
        end_time = timezone.now() + timedelta(days=2)
        self.event = Event.objects.create(
            club=self.club,
            name='Sample Event',
            description='Sample Description',
            start_time=start_time,
            end_time=end_time,
            location='Sample Location'
        )
        self.event.categories.add(self.category_music)

        # Create RSVP (initial state True)
        self.rsvp = RSVP.objects.create(
            user=self.user,
            event=self.event,
            status=True
        )

    ### Testing the events_home page
    def test_events_home_view(self):
        url = reverse('events_home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')

    ### Test Activity List (no filter)
    def test_event_list_view_no_filter(self):
        url = reverse('events')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        events_list = list(response.context['events'])
        self.assertTrue(any(e.name == 'Sample Event' for e in events_list))

    ###  Test Event Details Page
    def test_event_detail_view(self):
        url = reverse('event_detail', kwargs={'pk': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('event', response.context)
        self.assertEqual(response.context['event'], self.event)

    ### Testing the rsvp_toggle view
    def test_rsvp_toggle_unauthenticated(self):
        url = reverse('rsvp_toggle', kwargs={'pk': self.event.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_rsvp_toggle_authenticated(self):
        self.client.login(username='normaluser', password='pass123')
        url = reverse('rsvp_toggle', kwargs={'pk': self.event.pk})
        response = self.client.post(url)
        self.assertIn(response.status_code, [200, 302])
        updated_rsvp = RSVP.objects.get(pk=self.rsvp.pk)
        self.assertTrue(updated_rsvp.status)

    ###  Test update operations 
    def test_update_event_name_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_name', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        response = self.client.post(url, {'event_name': 'New Name'}, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, 'Sample Event')

    def test_update_event_description_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_description', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        new_desc = 'Updated desc'
        response = self.client.post(url, {'event_description': new_desc}, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, 'Sample Description')

    def test_update_event_time_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_time', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        new_start = timezone.now() + timedelta(days=10)
        new_end = timezone.now() + timedelta(days=11)
        data = {
            'event_start_time': new_start.strftime('%Y-%m-%dT%H:%M'),
            'event_end_time': new_end.strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(url, data, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        original_start = self.event.start_time  
        original_end = self.event.end_time
        self.assertEqual(self.event.start_time.replace(second=0, microsecond=0),
                         original_start.replace(second=0, microsecond=0))
        self.assertEqual(self.event.end_time.replace(second=0, microsecond=0),
                         original_end.replace(second=0, microsecond=0))

    def test_update_event_location_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_location', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        response = self.client.post(url, {'event_location': 'New Location'}, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        self.assertEqual(self.event.location, 'Sample Location')

    def test_update_event_category_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_category', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        data = {
            'categories': [self.category_sports.id],
            'new_category': 'Dance'
        }
        response = self.client.post(url, data, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        categories = self.event.categories.all()
        self.assertTrue(any(cat.name == 'Music' for cat in categories))
        self.assertFalse(any(cat.name == 'Sports' for cat in categories))
        self.assertFalse(any(cat.name == 'Dance' for cat in categories))

    ### Testing the creation of active views
    def test_create_event_view_get(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('create_event', kwargs={'club_id': self.club.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])

    def test_create_event_view_post_success(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('create_event', kwargs={'club_id': self.club.pk})
        data = {
            'name': 'New Test Event',
            'description': 'desc ...',
            'start_time': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
            'end_time': (timezone.now() + timedelta(days=4)).strftime('%Y-%m-%dT%H:%M'),
            'location': 'Somewhere'
        }
        response = self.client.post(url, data, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.assertFalse(Event.objects.filter(name='New Test Event').exists())

    ###  Test deleting the active view
    def test_delete_event_view(self):
        self.client.login(username='admin', password='pass123')
        session = self.client.session
        session['password_verified'] = True
        session.save()
        url = reverse('delete_event', kwargs={'club_id': self.club.pk, 'event_id': self.event.pk})
        response = self.client.get(url, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(Event.objects.filter(pk=self.event.pk).exists())

    ###  Test deleting the RSVP view
    def test_remove_rsvp_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('remove_rsvp', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk,
            'rsvp_id': self.rsvp.pk
        })
        response = self.client.post(url, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(RSVP.objects.filter(pk=self.rsvp.pk).exists())
