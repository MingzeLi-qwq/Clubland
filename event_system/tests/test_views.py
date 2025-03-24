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
        Create regular user, manager user, and admin user  
        Create a Club (this Club model does not include owner or managers fields)  
        Create two categories, one event, and one RSVP 
        """
        self.client = Client()

        # create three types of users
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
        # Create a user without membership
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

        # Create membership relations
        # Regular user as a normal member
        Membership.objects.create(
            user=self.user,
            club=self.club,
        )
        # Manager user as a club manager
        Membership.objects.create(
            user=self.manager_user,
            club=self.club,
            is_manager=True
        )

        # Create categories
        self.category_music = Category.objects.create(name='Music')
        self.category_sports = Category.objects.create(name='Sports')

        # Calculate event start and end times (timezone.now() returns a timezone-aware datetime)
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

        # Create RSVP (initial status is True)
        self.rsvp = RSVP.objects.create(
            user=self.user,
            event=self.event,
            status=True
        )

    def test_is_same_event_name_exist(self):
        from event_system.views import isSameEventNameExist
        # Create test event
        Event.objects.create(
            club=self.club,
            name="Test Event",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2)
        )
        # Test same name
        self.assertTrue(isSameEventNameExist("Test Event"))
        # Test name formatting (case and spaces)
        self.assertTrue(isSameEventNameExist(" test event "))
        self.assertTrue(isSameEventNameExist("TESTEVENT"))
        # Test non-existing name
        self.assertFalse(isSameEventNameExist("Non Existing Event"))
        # Test empty string
        self.assertFalse(isSameEventNameExist(""))

    ### Test events_home page
    def test_events_home_view(self):
        url = reverse('events_home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')

    ### Test event list view (no filters)
    def test_event_list_view_no_filter(self):
        url = reverse('events')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        events_list = list(response.context['events'])
        self.assertTrue(any(e.name == 'Sample Event' for e in events_list))

    ### Test event list view (with filters)
    def test_event_list_filters(self):
        try:
            # Create test data
            club = Club.objects.create(name="Test event list filters club")
            # Change the duplicate "Sports" to a unique name
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
            # Test search functionality
            response = self.client.get(reverse('events'), {'search': 'Future'})
            self.assertContains(response, 'Future Event')
            self.assertNotContains(response, 'Past Event')
            # Test date filter
            response = self.client.get(reverse('events'), {'date': 'upcoming'})
            self.assertContains(response, 'Sample Event')
            self.assertNotContains(response, 'Past Event')
            # Test club filter
            response = self.client.get(reverse('events'), {'club': club.pk})
            self.assertContains(response, 'Past Event')
            self.assertNotContains(response, 'Sample Event')
            # Test category filter
            response = self.client.get(reverse('events'), {'category': 'Test Sports'})  # Modified here
            self.assertContains(response, 'Future Event')
            self.assertNotContains(response, 'Sample Event')
        finally:
            # Clean up test data
            if 'future_event' in locals():
                future_event.delete()
            if 'past_event' in locals():
                past_event.delete()
            if 'club' in locals():
                club.delete()
            if 'category3' in locals():
                category3.delete()

    def test_rsvp_toggle_first_time(self):
        """Test first-time RSVP creation"""
        # Create a new test event to avoid conflict with existing RSVP from setUp
        test_event = Event.objects.create(
            club=self.club,
            name="RSVP Toggle Test Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        self.client.force_login(self.user)
        
        # Verify initial state does not have RSVP
        self.assertFalse(RSVP.objects.filter(user=self.user, event=test_event).exists())
        
        response = self.client.post(
            reverse('rsvp_toggle', args=[test_event.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify RSVP creation and status
        self.assertTrue(RSVP.objects.filter(user=self.user, event=test_event).exists())
        rsvp = RSVP.objects.get(user=self.user, event=test_event)
        self.assertEqual(response.json()['new_status'], True)
        self.assertTrue(rsvp.status)

    def test_rsvp_toggle_invalid_method(self):
        """Test non-POST request"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('rsvp_toggle', args=[self.event.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid request method', response.json()['message'])

    def test_rsvp_toggle_unauthenticated(self):
        """Test access by unauthenticated user"""
        response = self.client.post(
            reverse('rsvp_toggle', args=[self.event.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/login/?next={reverse('rsvp_toggle', args=[self.event.pk])}")

    ### Test event detail view
    def test_event_detail_view(self):
        url = reverse('event_detail', kwargs={'pk': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('event', response.context)
        self.assertEqual(response.context['event'], self.event)

    ### Test CreateEventView
    def test_create_event_as_manager(self): 
        """Test event creation by manager user"""
        # Login as manager user
        self.client.force_login(self.manager_user)
        
        # Prepare valid data
        valid_data = {
            'name': 'New Event',
            'description': 'Test Description',
            'start_time': (timezone.now() + timedelta(days=3)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=4)).isoformat(),
            'location': 'Test Location',
            'categories': [self.category_music.id]
        }
        
        # Send POST request
        response = self.client.post(
            reverse('create_event', args=[self.club.club_id]),
            data=valid_data
        )
        
        # Verify creation succeeded
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(Event.objects.filter(name='New Event').exists())

    def test_create_event_missing_required_fields(self):
        """Test creation request with missing required fields"""
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
        
        # Verify no new event created
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(Event.objects.count(), initial_count)
        self.assertContains(response, "Title, time and place are required") 

    def test_create_duplicate_event_name(self):
        """Test creating an event with a duplicate name"""
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
        
        # Verify duplicate creation is blocked
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(Event.objects.count(), initial_count)
        self.assertContains(response, "Event with the same name already exists")  

    def test_delete_event_post_without_verification(self):
        """Test the POST deletion request without password verification"""
        self.client.force_login(self.admin_user)
        test_event = Event.objects.create(
            club=self.club,
            name="POST Test Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Send POST request (without verification)
        response = self.client.post(
            reverse('delete_event', args=[self.club.club_id, test_event.pk]),
            follow=True
        )
        
        # Verify redirect to password verification page
        self.assertRedirects(response, reverse('verify_admin_password'))
        # Verify session stores correct values
        session = self.client.session
        self.assertEqual(session.get('pending_action'), 'delete_event')
        self.assertEqual(session.get('club_id'), self.club.club_id)
        self.assertEqual(session.get('event_id'), test_event.pk)

    def test_delete_event_post_with_verification(self):
        """Test the POST deletion request after password verification"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Manager POST Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Set verified session
        session = self.client.session
        session.update({
            'password_verified': True,
            'pending_action': 'delete_event',
            'club_id': self.club.club_id,
            'event_id': test_event.pk
        })
        session.save()
        
        # Send POST request
        response = self.client.post(
            reverse('delete_event', args=[self.club.club_id, test_event.pk]),
            follow=True
        )
        
        # Verify successful deletion and redirect to club manager page
        self.assertRedirects(response, reverse('club_manager_events', args=[self.club.club_id]))
        self.assertFalse(Event.objects.filter(pk=test_event.pk).exists())

    def test_update_event_name_duplicate(self):
        """Test updating event name to the same name"""
        self.client.force_login(self.admin_user)
        
        # Create original event
        test_event = Event.objects.create(
            club=self.club,
            name="Original Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Send update request with same name
        response = self.client.post(
            reverse('update_event_name', args=[self.club.club_id, test_event.pk]),
            {'event_name': 'Original Event'}, 
            follow=True
        )
        
        # Verify error message and name not changed
        self.assertContains(response, "The new name cannot duplicate the old name.")
        test_event.refresh_from_db()
        self.assertEqual(test_event.name, "Original Event")

    def test_update_event_name_empty(self):
        """Test updating event name to empty"""
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
        """Test updating event name to a name that conflicts with another event"""
        self.client.force_login(self.manager_user)
        
        # Create a conflicting event
        conflict_event = Event.objects.create(
            club=self.club,
            name="Existing Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Try updating another event to that same name
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
        """Test successful update of event name"""
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
        
        # Verify successful update
        test_event.refresh_from_db()
        self.assertEqual(test_event.name, "New Valid Name")
        self.assertRedirects(response, reverse('club_manager_event_general', args=[self.club.club_id, test_event.pk]))
        self.assertContains(response, "updated successfully")

    def test_update_description_duplicate(self):
        """Test updating description with the same value as before"""
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
        """Test updating description to an empty value"""
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
        """Test successful update of event description"""
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
        """Test updating event time with empty values"""
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
        """Test updating event time with end time earlier than start time"""
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
        """Test updating event with a start time in the past"""
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
        """Test successful update of event time"""
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
        """Test updating event location to an empty value"""
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
        """Test updating location with the same value as the original"""
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
        """Test successful update of event location"""
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
        """Test assigning existing categories to the event"""
        self.client.force_login(self.admin_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Category Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Use the music category created in setUp
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
        """Test creating a duplicate category"""
        self.client.force_login(self.manager_user)
        test_event = Event.objects.create(
            club=self.club,
            name="Duplicate Category Test",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Attempt to create a category that duplicates the one created in setUp (case-insensitive)
        response = self.client.post(
            reverse('update_event_category', args=[self.club.club_id, test_event.pk]),
            {
                'categories': [],
                'new_category': 'SPORTS'  # Use uppercase to test case-insensitive validation
            },
            follow=True
        )
        
        self.assertContains(response, "already exists")
        self.assertEqual(Category.objects.filter(name__iexact='sports').count(), 1)  

    def test_create_new_category_success(self):
        """Test successful creation of a new category"""
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
        """Global cleanup after all tests have run (only once)"""
        super().tearDownClass()
        # Clean up in dependency order (RSVP → Event → Club → User → Category)
        RSVP.objects.all().delete()
        Event.objects.all().delete()
        Membership.objects.all().delete()
        Club.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()