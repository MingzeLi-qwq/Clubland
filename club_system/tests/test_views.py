from django.test import TestCase, Client
from django.urls import reverse
from club_system.models import Club, Membership, NewClubRequest
from user_system.models import User
from event_system.models import Event, RSVP
from django.utils import timezone
from datetime import timedelta
from club_system.views import isSameClubNameExist, isSameClubNameExistInRequest

class ClubSystemViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            account_type="User"
        )
        
        self.user2 = User.objects.create_user(
            username="@testuse2r",
            email="test2@example.com",
            password="testpass123",
            first_name="Testtwo",
            last_name="User",
            account_type="User"
        )

        self.admin_user = User.objects.create_user(
            username="@adminuser",
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            account_type="Admin"
        )
        
        self.manager_user = User.objects.create_user(
            username="@manageruser",
            email="manager@example.com",
            password="managerpass123",
            first_name="Manager",
            last_name="User",
            account_type="User"
        )
        
        # Create a test club
        self.club = Club.objects.create(
            name="Test Club",
            description="Test Description"
        )
        
        # Creating a membership for a regular user as a manager
        self.manager_membership = Membership.objects.create(
            user=self.manager_user,
            club=self.club,
            is_manager=True
        )

        self.user2_membership = Membership.objects.create(
            user=self.user2,
            club=self.club,
        )

        # Create a Test Club Application
        self.club_request = NewClubRequest.objects.create(
            creator=self.user,
            name="New Test Club",
            description="New Test Description",
            status=NewClubRequest.STATUS_PENDING
        )

        # Create two test events
        self.event1 = Event.objects.create(
            name="Test Event 1",
            description="Test Event Description 1",
            club=self.club,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            location="Test Location 1"
        )
        
        self.event2 = Event.objects.create(
            name="Special Workshop",
            description="Test Event Description 2",
            club=self.club,
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=3),
            location="Test Location 2"
        )      
        

    def test_clubs_list_view(self):
        """Test Club List View"""
        response = self.client.get(reverse('clubs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        
        # Test the search function
        response = self.client.get(reverse('clubs'), {'search': 'Test'})
        self.assertContains(response, 'Test Club')
        
    def test_isSameClubNameExist(self):
        """Testing if the isSameClubNameExist function correctly detects duplicate club names"""
        # Test the exact same name
        self.assertTrue(isSameClubNameExist("Test Club"))
        
        # Testing different names
        self.assertFalse(isSameClubNameExist("Different Club"))
        
        # Tests Ignore Case
        self.assertTrue(isSameClubNameExist("TEST CLUB"))
        self.assertTrue(isSameClubNameExist("test club"))
        
        # Test Ignore Spaces
        self.assertTrue(isSameClubNameExist("TestClub"))
        self.assertTrue(isSameClubNameExist("Test  Club"))
        self.assertTrue(isSameClubNameExist(" Test Club "))
        
        # Test for ignoring both case and spaces
        self.assertTrue(isSameClubNameExist("TESTCLUB"))
        self.assertTrue(isSameClubNameExist("test  club"))
        



    def test_club_manager_members_view(self):
        """Test Club manager Member Page View"""
        self.client.login(username='@manageruser', password='managerpass123')
        
        response = self.client.get(reverse('club_manager_members', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_manager/members.html')

        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['manager_count'], 1)
        self.assertEqual(response.context['muggle_count'], 1)
        
    def test_club_manager_members_search(self):
        """Testing the search function on the club manager's member page"""
        self.client.login(username='@manageruser', password='managerpass123')

        # Test manager Search
        response = self.client.get(
            reverse('club_manager_members', args=[self.club.pk]),
            {'manager_search': 'Manager'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'manager@example.com')
        
        # Test Member Search
        response = self.client.get(
            reverse('club_manager_members', args=[self.club.pk]),
            {'member_search': 'Testtwo'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test2@example.com')
        
        # Test Mailbox Search
        response = self.client.get(
            reverse('club_manager_members', args=[self.club.pk]),
            {'member_search': 'test2@example.com'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Testtwo')
        
        # Test no result search
        response = self.client.get(
            reverse('club_manager_members', args=[self.club.pk]),
            {'member_search': 'NonExistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'test2@example.com')


    def test_club_manager_events_view(self):
        """Test Club manager Event Page View"""
        self.client.login(username='@manageruser', password='managerpass123')
        
        # Accessing the Event Management Page
        response = self.client.get(reverse('club_manager_events', args=[self.club.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_manager/events.html')
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(response.context['club'], self.club)
        
        self.assertEqual(len(response.context['events']), 2)
        self.assertContains(response, 'Test Event 1')
        self.assertContains(response, 'Special Workshop')
        
    def test_club_manager_events_search(self):
        """Testing the search function on the Club manager Events page"""
        self.client.login(username='@manageruser', password='managerpass123')

        # Test Event Name Search
        response = self.client.get(
            reverse('club_manager_events', args=[self.club.pk]),
            {'search': 'Special'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Special Workshop')
        self.assertNotContains(response, 'Test Event 1')
        
        # Test Date Search
        tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse('club_manager_events', args=[self.club.pk]),
            {'search': tomorrow}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event 1')
        self.assertNotContains(response, 'Special Workshop')
        
        # Test no result search
        response = self.client.get(
            reverse('club_manager_events', args=[self.club.pk]),
            {'search': 'NonExistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Event 1')
        self.assertNotContains(response, 'Special Workshop')

    
    def test_update_club_name(self):
        """Test updating club name functionality"""
        # Create another club for testing name duplication
        club2 = Club.objects.create(
            name="Test Club 2",
            description="Test Description 2"
        )
        
        # new name cannot duplicate old name
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'Test Club'}
        )
        self.assertEqual(self.club.name, "Test Club")
        
        # new name cannot be empty
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': ''}
        )
        self.assertEqual(self.club.name, "Test Club")
        
        # new names cannot duplicate existing club names
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'Test Club 2'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "Test Club")
        
        # The new name cannot duplicate the name of a request that is pending requirement
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'New Test Club'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "Test Club")
        
        # Successful name update
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'New Test Club Name'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "New Test Club Name")
        
        # Change the name back to the original
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'Test Club'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "Test Club")
        
        club2.delete()
        
    def test_update_club_description(self):
        """Test Update Club Description Feature"""
        # The new description cannot duplicate the old description
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('update_club_description', args=[self.club.pk]),
            {'club_description': 'Test Description'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, "Test Description")
        
        # A new description that is empty will use the default description
        response = self.client.post(
            reverse('update_club_description', args=[self.club.pk]),
            {'club_description': ''}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, "This Club hasn't added a Description yet")
        
        # Successfully updated description
        response = self.client.post(
            reverse('update_club_description', args=[self.club.pk]),
            {'club_description': 'New Test Club Description'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, "New Test Club Description")

    def test_remove_manager(self):
        """Test removing club manager functionality"""
        another_manager = User.objects.create_user(
            username="@anothermanager",
            email="another@example.com",
            password="managerpass123",
            first_name="Another",
            last_name="Manager",
            account_type="User"
        )
        
        # Make this user an manager
        another_manager_membership = Membership.objects.create(
            user=another_manager,
            club=self.club,
            is_manager=True
        )
        
        # Test admin User Remove manager
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('remove_manager', args=[self.club.pk, '@manageruser'])
        )
        
        membership = Membership.objects.get(user=self.manager_user, club=self.club)
        self.assertFalse(membership.is_manager)
        
        # Restore manager identity for subsequent testing
        membership.is_manager = True
        membership.save()
        
        # Test club manager removing another manager
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.post(
            reverse('remove_manager', args=[self.club.pk, '@anothermanager'])
        )
        another_membership = Membership.objects.get(user=another_manager, club=self.club)
        self.assertFalse(another_membership.is_manager)
        
        # Test removing the last manager will be denied
        response = self.client.post(
            reverse('remove_manager', args=[self.club.pk, '@manageruser'])
        )
        membership = Membership.objects.get(user=self.manager_user, club=self.club)
        self.assertTrue(membership.is_manager)
        
        another_manager_membership.delete()
        another_manager.delete()

    def test_set_manager_view(self):
        """Test setting up the club manager function"""
        normal_member = User.objects.create_user(
            username="@normalmember",
            email="normal@example.com",
            password="testpass123",
            first_name="Normal",
            last_name="Member",
            account_type="User"
        )
        
        # Creating Member Relationships (non-manager)
        normal_membership = Membership.objects.create(
            user=normal_member,
            club=self.club,
            is_manager=False
        )
        
        self.client.login(username='@manageruser', password='managerpass123')
        
        # Test setting regular members as manager
        response = self.client.post(
            reverse('set_manager', args=[self.club.pk, '@normalmember'])
        )
        normal_membership.refresh_from_db()
        self.assertTrue(normal_membership.is_manager)
        
        normal_member.delete()

    def test_remove_member_view(self):
        """Test removing the Club General Membership feature"""
        normal_member = User.objects.create_user(
            username="@normalmember",
            email="normal@example.com",
            password="testpass123",
            first_name="Normal",
            last_name="Member",
            account_type="User"
        )
        
        # Creating Member Relationships (non-manager)
        normal_membership = Membership.objects.create(
            user=normal_member,
            club=self.club,
            is_manager=False
        )
        
        self.client.login(username='@manageruser', password='managerpass123')
        
        # Test removing non-existent users
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@nonexistentuser'])
        )
        self.assertEqual(Membership.objects.filter(club=self.club).count(), 3)
        
        # Test removing manager will be denied
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@manageruser'])
        )
        self.assertTrue(Membership.objects.filter(user=self.manager_user, club=self.club).exists())
        
        # Successful test removes ordinary members
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@normalmember'])
        )
        self.assertFalse(Membership.objects.filter(user=normal_member, club=self.club).exists())
        
        normal_membership = Membership.objects.create(
            user=normal_member,
            club=self.club,
            is_manager=False
        )
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@normalmember'])
        )
        self.assertFalse(Membership.objects.filter(user=normal_member, club=self.club).exists())
        
        normal_member.delete()

    def test_club_manager_event_general_view(self):
        """Test Club manager events General information page view"""
        self.client.login(username='@manageruser', password='managerpass123')
        
        response = self.client.get(
            reverse('club_manager_event_general', args=[self.club.pk, self.event1.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_manager/event/general.html')
        
        # Test non-manager user access (should be redirected)
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(
            reverse('club_manager_event_general', args=[self.club.pk, self.event1.pk])
        )
        self.assertNotEqual(response.status_code, 200)

    def test_club_manager_event_rsvps_view(self):
        """Test Club manager Events RSVP List Page View"""
        # Create an RSVP record for testing
        rsvp = RSVP.objects.create(
            user=self.user,
            event=self.event1
        )
        
        self.client.login(username='@manageruser', password='managerpass123')
        
        response = self.client.get(
            reverse('club_manager_event_RSVPs', args=[self.club.pk, self.event1.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_manager/event/RSVPs.html')
        
        # Test the search function
        response = self.client.get(
            reverse('club_manager_event_RSVPs', args=[self.club.pk, self.event1.pk]),
            {'search': 'Test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rsvps']), 1)
        
        # Test no result search
        response = self.client.get(
            reverse('club_manager_event_RSVPs', args=[self.club.pk, self.event1.pk]),
            {'search': 'NonExistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rsvps']), 0)
        
        # Test non-manager user access (should be redirected)
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(
            reverse('club_manager_event_RSVPs', args=[self.club.pk, self.event1.pk])
        )
        self.assertNotEqual(response.status_code, 200)
        
        rsvp.delete()

    def test_apply_new_club_view_get(self):
        """Testing GET requests for requesting new club pages"""
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('apply_new_club'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'apply_new_club.html')
        self.assertTrue('form' in response.context)
        
        # Testing unlogged user access (should be redirected)
        self.client.logout()
        response = self.client.get(reverse('apply_new_club'))
        self.assertNotEqual(response.status_code, 200) 

    def test_apply_new_club_view_post(self):
        """Testing POST requests for requesting a new club page"""
        self.client.login(username='@testuser', password='testpass123')
        
        # Test submission of valid forms
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': 'Brand New Club',
                'description': 'This is a brand new club for testing'
            }
        )
        
        # Check if a new club request has been created
        self.assertTrue(NewClubRequest.objects.filter(name='Brand New Club').exists())
        new_request = NewClubRequest.objects.get(name='Brand New Club')
        self.assertEqual(new_request.creator, self.user)
        self.assertEqual(new_request.description, 'This is a brand new club for testing')
        self.assertEqual(new_request.status, NewClubRequest.STATUS_PENDING)
        
        # Test submitting a form that renames an existing club
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': 'Test Club',
                'description': 'This should fail'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A club with this name already exists")
        
        # Test submitting a form that is renamed with a pending review request
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': 'New Test Club',
                'description': 'This should also fail'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['form'].errors)
        
        # Test submitting a form with an empty name
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': '',
                'description': 'This should fail due to empty name'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['form'].errors)
        
        # Test for unlogged user submissions (should be redirected)
        self.client.logout()
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': 'Another New Club',
                'description': 'This should fail due to not logged in'
            }
        )
        self.assertNotEqual(response.status_code, 200)
        
        # Check if no new club application has been created
        self.assertFalse(NewClubRequest.objects.filter(name='Another New Club').exists())

    @classmethod
    def tearDownClass(cls):
        """clean up test cases"""
        super().tearDownClass()
        User.objects.all().delete()
        Club.objects.all().delete()
        Membership.objects.all().delete()
        NewClubRequest.objects.all().delete()
        Event.objects.all().delete()