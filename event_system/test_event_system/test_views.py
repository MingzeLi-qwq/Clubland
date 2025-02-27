# test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model

from club_system.models import Club
from event_system.models import Category, Event, RSVP

User = get_user_model()


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(name="Test Club")
        self.category = Category.objects.create(name="Sports")
        
        # 使用未来时间，确保事件满足视图过滤条件 (start_time__gte=timezone.now())
        start_time_featured = timezone.now() + timedelta(days=1)
        end_time_featured = start_time_featured + timedelta(hours=2)
        self.featured_event = Event.objects.create(
            name="Featured Event",
            club=self.club,
            start_time=start_time_featured,
            end_time=end_time_featured,
            location="Location A",
            description="Featured event description",
            is_featured=True,
        )
        self.featured_event.categories.add(self.category)
        
        start_time_upcoming = timezone.now() + timedelta(days=2)
        end_time_upcoming = start_time_upcoming + timedelta(hours=2)
        self.upcoming_event = Event.objects.create(
            name="Upcoming Event",
            club=self.club,
            start_time=start_time_upcoming,
            end_time=end_time_upcoming,
            location="Location B",
            description="Upcoming event description",
            is_featured=False,
        )
        self.upcoming_event.categories.add(self.category)
    
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shared/home.html')
        
        # 直接检查渲染后的 HTML 内容
        content = response.content.decode('utf-8')
        # 断言 'Featured Event' 出现在首页
        self.assertIn(self.featured_event.name, content)
        # 断言 'Upcoming Event' 出现在首页
        #self.assertIn(self.upcoming_event.name, content)


class EventsHomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_events_home_view(self):
        response = self.client.get(reverse('events_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')


class EventListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(name="Test Club")
        # 使用 datetime + timezone.make_aware 创建固定时间 (过去时间)
        start_time = timezone.make_aware(datetime(2023, 1, 1, 10, 0, 0))
        end_time = timezone.make_aware(datetime(2023, 1, 1, 12, 0, 0))
        self.event1 = Event.objects.create(
            name="Test Event One",
            club=self.club,
            start_time=start_time,
            end_time=end_time,
            location="Location One",
            description="Description One",
            is_featured=False,
        )
        self.event2 = Event.objects.create(
            name="Another Event",
            club=self.club,
            start_time=start_time + timedelta(days=1),
            end_time=end_time + timedelta(days=1),
            location="Location Two",
            description="Description Two",
            is_featured=True,
        )
    
    def test_event_list_view_without_filters(self):
        response = self.client.get(reverse('events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')
        self.assertIn('events', response.context)
        self.assertGreaterEqual(len(response.context['events']), 2)
    
    def test_event_list_view_with_search(self):
        response = self.client.get(reverse('events'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        events = response.context['events']
        self.assertIn(self.event1, events)
        self.assertNotIn(self.event2, events)


class EventDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(name="Test Club")
        start_time = timezone.make_aware(datetime(2023, 1, 1, 10, 0, 0))
        end_time = timezone.make_aware(datetime(2023, 1, 1, 12, 0, 0))
        self.event = Event.objects.create(
            name="Detail Event",
            club=self.club,
            start_time=start_time,
            end_time=end_time,
            location="Detail Location",
            description="Detail description",
            is_featured=False,
        )
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_event_detail_anonymous(self):
        response = self.client.get(reverse('event_detail', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')
        self.assertIsNone(response.context.get('user_rsvp'))
    
    def test_event_detail_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        RSVP.objects.create(user=self.user, event=self.event, status=True)
        response = self.client.get(reverse('event_detail', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')
        self.assertIsNotNone(response.context.get('user_rsvp'))


class RSVPViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(name="Test Club")
        start_time = timezone.make_aware(datetime(2023, 1, 1, 10, 0, 0))
        end_time = timezone.make_aware(datetime(2023, 1, 1, 12, 0, 0))
        self.event = Event.objects.create(
            name="RSVP Event",
            club=self.club,
            start_time=start_time,
            end_time=end_time,
            location="RSVP Location",
            description="RSVP description",
            is_featured=False,
        )
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_rsvp_toggle_invalid_method(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('rsvp_toggle', args=[self.event.id]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('status'), 'error')
    
    def test_rsvp_toggle_create_and_toggle(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('rsvp_toggle', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertTrue(data.get('new_status'))
        
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertFalse(data2.get('new_status'))
