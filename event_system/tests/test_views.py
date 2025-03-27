from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from user_system.models import User
from club_system.models import Club, Membership
from event_system.models import Event, RSVP, Category

class EventsViewsTest(TestCase):
    def setUp(self):
        """
        Create a regular user, manager user, admin user
        Create a Club (here the Club model does not contain an owner or managers field)
        Create two categories, an event, and an RSVP
        """
        self.client = Client()

        # Create three types of users
        self.user = User.objects.create_user(
            username='@normaluser',
            email='normal@example.com',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_USER,
            first_name='Normal',
            last_name='User'
        )
        self.manager_user = User.objects.create_user(
            username='@manager',
            email='manager@example.com',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_USER,
            first_name='Manager',
            last_name='User'
        )
        self.admin_user = User.objects.create_user(
            username='@admin',
            email='admin@example.com',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_ADMIN,
            first_name='Admin',
            last_name='User'
        )
        # Create regular users with no membership relationship
        self.non_membership_user = User.objects.create_user(
            username='@nonmember',
            email='nonmember@example.com',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_USER,
            first_name='Nonmember',
            last_name='User'
        )
    

        # Create a Club
        self.club = Club.objects.create(name='Test Club')

        # Creating Member Relationships
        Membership.objects.create(
            user=self.user,
            club=self.club,
        )
        Membership.objects.create(
            user=self.manager_user,
            club=self.club,
            is_manager=True
        )

        # Create Category
        self.category_music = Category.objects.create(name='Music')
        self.category_sports = Category.objects.create(name='Sports')

        # Calculate event start and end times
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

        # make RSVP
        self.rsvp = RSVP.objects.create(
            user=self.user,
            event=self.event,
            status=True
        )

    def test_is_same_event_name_exist(self):
        from event_system.views import isSameEventNameExist
        Event.objects.create(
            club=self.club,
            name="Test Event",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2)
        )

        self.assertTrue(isSameEventNameExist("Test Event"))

        self.assertTrue(isSameEventNameExist(" test event "))
        self.assertTrue(isSameEventNameExist("TESTEVENT"))

        self.assertFalse(isSameEventNameExist("Non Existing Event"))

        self.assertFalse(isSameEventNameExist(""))

    ### test events page
    def test_events_home_view(self):
        url = reverse('events_home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')

    ### Test event List (no filter)
    def test_event_list_view_no_filter(self):
        url = reverse('events')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        events_list = list(response.context['events'])
        self.assertTrue(any(e.name == 'Sample Event' for e in events_list))

    ### Test event List (with filter)
    def test_event_list_filters(self):
        try:
            club = Club.objects.create(name="Test event list filters club")
            category3 = Category.objects.create(name="Test Sports")
            future_event = Event.objects.create(
                club=self.club,
                name="Future Event",
                start_time=timezone.now() + timedelta(days=3),
                end_time=timezone.now() + timedelta(days=4),
                location="Test Location"
            )
            past_event = Event.objects.create(
                club=club,
                name="Past Event",
                start_time=timezone.now() - timedelta(days=3),
                end_time=timezone.now() - timedelta(days=2),
                location="Test Location"
            )
            future_event.categories.add(category3) 
            
            response = self.client.get(reverse('events'), {'search': 'Future'})
            self.assertContains(response, 'Future Event')
            self.assertNotContains(response, 'Past Event')
            
            response = self.client.get(reverse('events'), {'date': 'upcoming'})
            self.assertContains(response, 'Sample Event')
            self.assertNotContains(response, 'Past Event')
            
            response = self.client.get(reverse('events'), {'club': club.pk})
            self.assertContains(response, 'Past Event')
            self.assertNotContains(response, 'Sample Event')

            response = self.client.get(reverse('events'), {'category': 'Test Sports'})   
            self.assertContains(response, 'Future Event')
            self.assertNotContains(response, 'Sample Event')
        finally:
            if 'future_event' in locals():
                future_event.delete()
            if 'past_event' in locals():
                past_event.delete()
            if 'club' in locals():
                club.delete()
            if 'category3' in locals():
                category3.delete()

    def test_rsvp_toggle_first_time(self):
        """Testing the first creation of an RSVP"""
        test_event = Event.objects.create(
            club=self.club,
            name="RSVP Toggle Test Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        self.client.force_login(self.user)
        
        self.assertFalse(RSVP.objects.filter(user=self.user, event=test_event).exists())
        
        response = self.client.post(
            reverse('rsvp_toggle', args=[test_event.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
         
        self.assertTrue(RSVP.objects.filter(user=self.user, event=test_event).exists())
        rsvp = RSVP.objects.get(user=self.user, event=test_event)
        self.assertEqual(response.json()['new_status'], True)
        self.assertTrue(rsvp.status)

    def test_rsvp_toggle_invalid_method(self):
        """Testing non-POST requests"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('rsvp_toggle', args=[self.event.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid request method', response.json()['message'])

    def test_rsvp_toggle_unauthenticated(self):
        """Test access for non-logged-in users"""
        response = self.client.post(
            reverse('rsvp_toggle', args=[self.event.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/login/?next={reverse('rsvp_toggle', args=[self.event.pk])}")

    def test_event_detail_view(self):
        url = reverse('event_detail', kwargs={'pk': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('event', response.context)
        self.assertEqual(response.context['event'], self.event)

    def test_create_event_as_manager(self): 
        """Test Amanager User Creation Activity"""
        self.client.force_login(self.manager_user)
        
        valid_data = {
            'name': 'New Event',
            'description': 'Test Description',
            'start_time': (timezone.now() + timedelta(days=3)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=4)).isoformat(),
            'location': 'Test Location',
            'categories': [self.category_music.id]
        }
        
        response = self.client.post(
            reverse('create_event', args=[self.club.club_id]),
            data=valid_data
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(name='New Event').exists())

    def test_create_event_missing_required_fields(self):
        """测试缺少必填字段的创建请求"""
        self.client.force_login(self.manager_user)
        
        invalid_data = {
            'description': 'Missing required fields',
            'start_time': (timezone.now() + timedelta(days=3)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=4)).isoformat(),
            'location': 'Test Location'
        }
        
        initial_count = Event.objects.count()
        response = self.client.post(
            reverse('create_event', args=[self.club.club_id]),
            data=invalid_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), initial_count)
        self.assertContains(response, "Title, time and place are required")

    def test_create_duplicate_event_name(self):
        """测试重复事件名称的创建"""
        self.client.force_login(self.manager_user)
        
        duplicate_data = {
            'name': 'Sample Event',
            'description': 'Duplicate Event',
            'start_time': (timezone.now() + timedelta(days=5)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=6)).isoformat(),
            'location': 'Duplicate Location'
        }
        
        initial_count = Event.objects.count()
        response = self.client.post(
            reverse('create_event', args=[self.club.club_id]),
            data=duplicate_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), initial_count)
        self.assertContains(response, "Event with the same name already exists")

    def test_delete_event_post_without_verification(self):
        """测试未验证密码的POST请求流程"""
        self.client.force_login(self.admin_user)
        test_event = Event.objects.create(
            club=self.club,
            name="POST Test Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('delete_event', args=[self.club.club_id, test_event.pk]),
            follow=True
        )
        
        self.assertRedirects(response, reverse('verify_admin_password'))
        session = self.client.session
        self.assertEqual(session.get('pending_action'), 'delete_event')
        self.assertEqual(session.get('club_id'), self.club.club_id)
        self.assertEqual(session.get('event_id'), test_event.pk)

    def test_delete_event_post_with_verification(self):
        """测试已验证密码的POST请求流程"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Manager POST Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        session = self.client.session
        session.update({
            'password_verified': True,
            'pending_action': 'delete_event',
            'club_id': self.club.club_id,
            'event_id': test_event.pk
        })
        session.save()
        
        response = self.client.post(
            reverse('delete_event', args=[self.club.club_id, test_event.pk]),
            follow=True
        )
        
        self.assertRedirects(response, reverse('club_manager_events', args=[self.club.club_id]))
        self.assertFalse(Event.objects.filter(pk=test_event.pk).exists())

    def test_update_event_name_duplicate(self):
        """测试更新事件名称时名称重复的情况"""
        self.client.force_login(self.admin_user)
        
        test_event = Event.objects.create(
            club=self.club,
            name="Original Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_name', args=[self.club.club_id, test_event.pk]),
            {'event_name': 'Original Event'},
            follow=True
        )
        
        # 验证错误消息和未更新
        self.assertContains(response, "The new name cannot duplicate the old name.")
        test_event.refresh_from_db()
        self.assertEqual(test_event.name, "Original Event")

    def test_update_event_name_empty(self):
        """测试更新事件名称为空的情况"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Test Empty Name",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_name', args=[self.club.club_id, test_event.pk]),
            {'event_name': ''},
            follow=True
        )
        
        self.assertContains(response, "Event name cannot be empty.")
        test_event.refresh_from_db()
        self.assertEqual(test_event.name, "Test Empty Name")

    def test_update_event_name_conflict(self):
        """测试新名称与其他事件冲突的情况"""
        self.client.force_login(self.manager_user)
        
        conflict_event = Event.objects.create(
            club=self.club,
            name="Existing Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        test_event = Event.objects.create(
            club=self.club,
            name="Unique Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_name', args=[self.club.club_id, test_event.pk]),
            {'event_name': 'Existing Event'},
            follow=True
        )
        
        self.assertContains(response, "already an Event with the same name")
        test_event.refresh_from_db()
        self.assertEqual(test_event.name, "Unique Event")

    def test_update_event_name_success(self):
        """测试成功更新事件名称"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Old Event Name",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_name', args=[self.club.club_id, test_event.pk]),
            {'event_name': 'New Valid Name'},
            follow=True
        )
        
        test_event.refresh_from_db()
        self.assertEqual(test_event.name, "New Valid Name")
        self.assertRedirects(response, reverse('club_manager_event_general', args=[self.club.club_id, test_event.pk]))
        self.assertContains(response, "updated successfully")

    def test_update_description_duplicate(self):
        """测试更新描述与原描述相同的情况"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Description Test",
            description="Initial Description",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_description', args=[self.club.club_id, test_event.pk]),
            {'event_description': "Initial Description"},
            follow=True
        )
        
        self.assertContains(response, "The new description cannot be the same as the old one.")
        test_event.refresh_from_db()
        self.assertEqual(test_event.description, "Initial Description")

    def test_update_description_empty(self):
        """测试更新描述为空的情况"""
        self.client.force_login(self.admin_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Empty Description Test",
            description="Initial Description",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_description', args=[self.club.club_id, test_event.pk]),
            {'event_description': ''},
            follow=True
        )
        
        self.assertContains(response, "Event Description cannot be empty.")
        test_event.refresh_from_db()
        self.assertEqual(test_event.description, "Initial Description")

    def test_update_description_success(self):
        """测试成功更新事件描述"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Success Description Test",
            description="Initial Description",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_description', args=[self.club.club_id, test_event.pk]),
            {'event_description': 'New Valid Description'},
            follow=True
        )
        
        test_event.refresh_from_db()
        self.assertEqual(test_event.description, "New Valid Description")
        self.assertRedirects(response, reverse('club_manager_event_general', args=[self.club.club_id, test_event.pk]))
        self.assertContains(response, "Event description updated successfully.")

    def test_update_time_empty_values(self):
        """测试空时间值的情况"""
        self.client.force_login(self.admin_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Empty Time Test",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2)
        )
        
        response = self.client.post(
            reverse('update_event_time', args=[self.club.club_id, test_event.pk]),
            {'event_start_time': '', 'event_end_time': ''},
            follow=True
        )
        
        self.assertContains(response, "Both start and end times are required")
        test_event.refresh_from_db()
        self.assertNotEqual(test_event.start_time, timezone.now())

    def test_update_time_invalid_order(self):
        """测试结束时间早于开始时间的情况"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Invalid Time Order",
            start_time=timezone.now() + timedelta(hours=3),
            end_time=timezone.now() + timedelta(hours=4)
        )
        
        invalid_time = (timezone.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(
            reverse('update_event_time', args=[self.club.club_id, test_event.pk]),
            {
                'event_start_time': invalid_time,
                'event_end_time': (timezone.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
            },
            follow=True
        )
        
        self.assertContains(response, "End time must be after start time")

    def test_update_past_start_time(self):
        """测试更新为过去开始时间的情况"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Past Start Time",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2)
        )
        
        past_time = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(
            reverse('update_event_time', args=[self.club.club_id, test_event.pk]),
            {
                'event_start_time': past_time,
                'event_end_time': (timezone.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
            },
            follow=True
        )
        
        self.assertContains(response, "Start time cannot be in the past")

    def test_update_time_success(self):
        """测试成功更新时间的情况"""
        self.client.force_login(self.manager_user)
        original_start = timezone.now() + timedelta(days=1)
        test_event = Event.objects.create(
            club=self.club,
            name="Time Update Test",
            start_time=original_start,
            end_time=original_start + timedelta(hours=2)
        )
        
        new_start = (original_start + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")
        new_end = (original_start + timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M")
        
        response = self.client.post(
            reverse('update_event_time', args=[self.club.club_id, test_event.pk]),
            {
                'event_start_time': new_start,
                'event_end_time': new_end
            },
            follow=True
        )
        
        test_event.refresh_from_db()
        self.assertEqual(test_event.start_time.strftime("%Y-%m-%dT%H:%M"), new_start)
        self.assertEqual(test_event.end_time.strftime("%Y-%m-%dT%H:%M"), new_end)
        self.assertRedirects(response, reverse('club_manager_event_general', args=[self.club.club_id, test_event.pk]))

    def test_update_location_empty(self):
        """测试更新地点为空的情况"""
        self.client.force_login(self.admin_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Empty Location Test",
            location="Initial Location",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_location', args=[self.club.club_id, test_event.pk]),
            {'event_location': ''},
            follow=True
        )
        
        self.assertContains(response, "cannot be empty")
        test_event.refresh_from_db()
        self.assertEqual(test_event.location, "Initial Location")

    def test_update_location_duplicate(self):
        """测试更新地点与原地点相同的情况"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Duplicate Location Test",
            location="Initial Location",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_location', args=[self.club.club_id, test_event.pk]),
            {'event_location': 'Initial Location'},
            follow=True
        )
        
        self.assertContains(response, "cannot be the same as the current one")
        test_event.refresh_from_db()
        self.assertEqual(test_event.location, "Initial Location")

    def test_update_location_success(self):
        """测试成功更新事件地点"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Success Location Test",
            location="Initial Location",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_location', args=[self.club.club_id, test_event.pk]),
            {'event_location': 'New Valid Location'},
            follow=True
        )
        
        test_event.refresh_from_db()
        self.assertEqual(test_event.location, "New Valid Location")
        self.assertRedirects(response, reverse('club_manager_event_general', args=[self.club.club_id, test_event.pk]))
        self.assertContains(response, "location updated successfully")

    def test_set_existing_categories(self):
        """测试设置已有分类"""
        self.client.force_login(self.admin_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Category Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_category', args=[self.club.club_id, test_event.pk]),
            {'categories': [str(self.category_music.id)]},
            follow=True
        )
        
        test_event.refresh_from_db()
        self.assertEqual(test_event.categories.count(), 1)
        self.assertEqual(test_event.categories.first().name, "Music")
        self.assertRedirects(response, reverse('admin_panel_club_event_general', args=[self.club.club_id, test_event.pk]))

    def test_create_duplicate_category(self):
        """测试创建重复分类"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Duplicate Category Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_category', args=[self.club.club_id, test_event.pk]),
            {
                'categories': [],
                'new_category': 'SPORTS'
            },
            follow=True
        )
        
        self.assertContains(response, "already exists")
        self.assertEqual(Category.objects.filter(name__iexact='sports').count(), 1)

    def test_create_new_category_success(self):
        """测试成功创建新分类"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="New Category Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        response = self.client.post(
            reverse('update_event_category', args=[self.club.club_id, test_event.pk]),
            {
                'categories': [str(self.category_music.id)],
                'new_category': 'Art'
            },
            follow=True
        )
        
        test_event.refresh_from_db()
        self.assertEqual(test_event.categories.count(), 2)
        self.assertTrue(test_event.categories.filter(name__in=["Music", "Art"]).exists())
        self.assertContains(response, "categories updated successfully")


    @classmethod
    def tearDownClass(cls):
        """在所有测试完成后执行全局清理（仅执行一次）"""
        super().tearDownClass()
        RSVP.objects.all().delete()
        Event.objects.all().delete()
        Membership.objects.all().delete()
        Club.objects.all().delete() 
        Category.objects.all().delete()
        User.objects.all().delete()
