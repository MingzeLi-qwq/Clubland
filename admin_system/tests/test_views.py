from django.test import TestCase, Client
from django.urls import reverse
from user_system.models import User
from club_system.models import Club, Membership, NewClubRequest
from event_system.models import Event, RSVP
from django.utils import timezone
from datetime import timedelta

class AdminSystemViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Creating an Administrator User
        self.admin_user = User.objects.create_user(
            username="@adminuser",
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            account_type="Admin"
        )
        
        # Creating an ordinary user
        self.normal_user = User.objects.create_user(
            username="@normaluser",
            email="normal@example.com",
            password="normalpass123",
            first_name="Normal",
            last_name="User",
            account_type="User"
        )
        
        # Creating Club Manager Users
        self.club_manager = User.objects.create_user(
            username="@clubmanager",
            email="manager@example.com",
            password="managerpass123",
            first_name="Club",
            last_name="Manager",
            account_type="User"
        )
        
        # Create a test club
        self.club = Club.objects.create(
            name="Test Club",
            description="Test Description"
        )
        
        # Create another test club
        self.another_club = Club.objects.create(
            name="Another Club",
            description="Another Description"
        )
        
        # Creating Member Relationships
        self.manager_membership = Membership.objects.create(
            user=self.club_manager,
            club=self.club,
            is_manager=True
        )
        
        self.member_membership = Membership.objects.create(
            user=self.normal_user,
            club=self.club,
            is_manager=False
        )
        
        # Creating test events
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Event Description",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            location="Test Location",
            club=self.club
        )

    def test_admin_panel_clubs_view(self):
        """Test Admin Panel Club List View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Visit the Club Listings page
        response = self.client.get(reverse('admin_panel_clubs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/clubs.html')
        
        # Test Search Function - Search for Existing Clubs
        response = self.client.get(reverse('admin_panel_clubs'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clubs']), 1)
        self.assertEqual(response.context['clubs'][0].name, 'Test Club')
        
        # Testing the search function - searching for non-existing clubs
        response = self.client.get(reverse('admin_panel_clubs'), {'search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clubs']), 0)

    def test_admin_panel_users_view(self):
        """Testing the Admin Panel User List View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Accessing the user list page
        response = self.client.get(reverse('admin_panel_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/users.html')
        
        # Testing the search function - searching for existing users
        response = self.client.get(reverse('admin_panel_users'), {'search': 'Normal'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 1)
        self.assertEqual(response.context['users'][0].username, '@normaluser')
        
        # Testing the search function - searching for non-existent users
        response = self.client.get(reverse('admin_panel_users'), {'search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 0)

    def test_admin_panel_requests_view(self):
        """Testing the admin panel request list view"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Accessing the request list page
        response = self.client.get(reverse('admin_panel_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/requests.html')

    def test_admin_panel_clubs_general_view(self):
        """Test Admini Panel Club General Information View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        response = self.client.get(reverse('admin_panel_club_general', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/general.html')
        
        self.assertIn('club', response.context)
        self.assertIn('club_id', response.context)
        self.assertEqual(response.context['club'].name, 'Test Club')
        self.assertEqual(response.context['club_id'], self.club.pk)

    def test_admin_panel_clubs_members_view(self):
        """Test Admin Panel Club Member List View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Visit the Club Membership List page
        response = self.client.get(reverse('admin_panel_club_members', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/members.html')
        
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['manager_count'], 1)
        self.assertEqual(response.context['muggle_count'], 1)
        
        # Test manager Search Function
        response = self.client.get(reverse('admin_panel_club_members', args=[self.club.pk]), {'manager_search': 'Club'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['managers']), 1)
        self.assertEqual(response.context['managers'][0].user.username, '@clubmanager')
        
        # Testing the general member search function
        response = self.client.get(reverse('admin_panel_club_members', args=[self.club.pk]), {'member_search': 'Normal'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['muggles']), 1)
        self.assertEqual(response.context['muggles'][0].user.username, '@normaluser')
        
        # Test search for non-existent members
        response = self.client.get(reverse('admin_panel_club_members', args=[self.club.pk]), {'member_search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['muggles']), 0)

    def test_admin_panel_clubs_news_view(self):
        """Test Admin Panel Club News View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        response = self.client.get(reverse('admin_panel_club_news', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/news.html')
        
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['club_id'], self.club.pk)

    def test_admin_panel_clubs_forum_view(self):
        """Test Admin Panel Club Forum View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        response = self.client.get(reverse('admin_panel_club_forum', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/forum.html')
        
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['club_id'], self.club.pk)

    def test_admin_panel_clubs_dashboard_view(self):
        """Test Admin Panel Club Dashboard View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        response = self.client.get(reverse('admin_panel_club_dashboard', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/dashboard.html')
        
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['club_id'], self.club.pk)

    def test_admin_panel_clubs_events_view(self):
        """Test Admin Panel Club Event List View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Create another test event for testing the search function
        another_event = Event.objects.create(
            name="Another Event",
            description="Another Event Description",
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=2),
            location="Another Location",
            club=self.club
        )
        
        # Visit the Club Event Listings page
        response = self.client.get(reverse('admin_panel_club_events', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/events.html')
        
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(len(response.context['events']), 2)  # 应该有两个事件
        
        # Testing the Search Function - Searching for Existing Events
        response = self.client.get(reverse('admin_panel_club_events', args=[self.club.pk]), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events']), 1)
        self.assertEqual(response.context['events'][0].name, 'Test Event')
        
        # Testing the search function - searching for non-existing events
        response = self.client.get(reverse('admin_panel_club_events', args=[self.club.pk]), {'search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events']), 0)
        
        another_event.delete()

    def test_admin_delete_club_view(self):
        """Test Admin Delete Club feature"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Create a new club for testing the delete function
        test_delete_club = Club.objects.create(
            name="Test Delete Club",
            description="This club will be deleted"
        )
        
        # Testing POST requests when password is not verified
        response = self.client.post(reverse('admin_delete_club', args=[test_delete_club.pk]))
        # Should redirect to the password verification page
        self.assertRedirects(response, reverse('verify_admin_password'))
        
        # Check that the correct value is set in the session
        self.assertEqual(self.client.session['pending_action'], 'delete_club')
        self.assertEqual(self.client.session['club_id'], test_delete_club.pk)
        self.assertEqual(
            self.client.session['return_url'], 
            reverse('admin_panel_club_general', kwargs={'club_id': test_delete_club.pk})
        )
        
        # Successful simulated password authentication - using a new session
        session = self.client.session
        session['password_verified'] = True
        session.save()
        
        # Testing GET requests with verified passwords
        response = self.client.get(reverse('admin_delete_club', args=[test_delete_club.pk]))
        self.assertRedirects(response, reverse('admin_panel_clubs'))
        self.assertEqual(Club.objects.filter(pk=test_delete_club.pk).count(), 0)
        self.assertNotIn('password_verified', self.client.session)

    def test_admin_panel_clubs_event_general_view(self):
        """Test Administrator Panel Club Event Detail View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        response = self.client.get(reverse('admin_panel_club_event_general', args=[self.club.pk, self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/admin_panel_club_event/general.html')

        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['event'], self.event)
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(response.context['event_id'], self.event.pk)

    def test_admin_panel_clubs_event_rsvps_view(self):
        """Test Administrator Panel Club Event RSVP list view"""
        self.client.login(username='@adminuser', password='adminpass123')
        # Creating a Test RSVP
        test_rsvp = RSVP.objects.create(
            user=self.normal_user,
            event=self.event
        )
        
        # Create another user and RSVP for testing the search function
        another_user = User.objects.create_user(
            username="@searchuser",
            email="search@example.com",
            password="searchpass123",
            first_name="Search",
            last_name="User",
            account_type="User"
        )
        
        another_rsvp = RSVP.objects.create(
            user=another_user,
            event=self.event
        )
        
        # Visit the Event RSVP List page
        response = self.client.get(reverse('admin_panel_club_event_RSVPs', args=[self.club.pk, self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/admin_panel_club_event/RSVPs.html')
        
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['event'], self.event)
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(len(response.context['rsvps']), 2)
        
        # Testing the search function - searching for existing users
        response = self.client.get(
            reverse('admin_panel_club_event_RSVPs', args=[self.club.pk, self.event.pk]), 
            {'search': 'Search'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rsvps']), 1)
        self.assertEqual(response.context['rsvps'][0].user.first_name, 'Search')
        
        # Testing the search function - searching for non-existent users
        response = self.client.get(
            reverse('admin_panel_club_event_RSVPs', args=[self.club.pk, self.event.pk]), 
            {'search': 'NonExistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rsvps']), 0)
        
        test_rsvp.delete()
        another_rsvp.delete()
        another_user.delete()

    def test_admin_panel_user_information_view(self):
        """Testing the Administrator Panel User Information View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        response = self.client.get(reverse('admin_panel_user_information', args=[self.normal_user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_user/information.html')
        
        self.assertEqual(response.context['panel_user'], self.normal_user)
        self.assertEqual(response.context['panel_username'], self.normal_user.username)

    def test_admin_panel_user_memberships_view(self):
        """Test Administrator Panel User Membership View"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Create another club and membership for testing
        another_club = Club.objects.create(
            name="Another Test Club",
            description="Another Test Club Description"
        )
        
        # Create a new membership for a regular user (in another club)
        regular_membership = Membership.objects.create(
            user=self.normal_user,
            club=another_club,
            is_manager=False
        )
        
        # Visit the User Membership page
        response = self.client.get(reverse('admin_panel_user_memberships', args=[self.normal_user.username]))
        
        # Check the response status code
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_user/memberships.html')

        self.assertEqual(response.context['panel_user'], self.normal_user)
        self.assertEqual(response.context['panel_username'], self.normal_user.username)
        
        # Check the number and type of memberships
        managers = response.context['managers']
        regulars = response.context['regulars']
        
        self.assertEqual(response.context['manager_count'], 0)  
        self.assertEqual(response.context['regular_count'], 2) 
        
        # Test the search function
        response = self.client.get(
            reverse('admin_panel_user_memberships', args=[self.normal_user.username]),
            {'search': 'Another Test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['manager_count'], 0)
        self.assertEqual(response.context['regular_count'], 1)
        self.assertEqual(response.context['regulars'][0].club.name, 'Another Test Club')
        
        regular_membership.delete()
        another_club.delete()

    def test_admin_panel_remove_memberships_view(self):
        """Test the administrator's ability to delete a user's membership"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Confirm that the membership has been created
        self.assertEqual(
            Membership.objects.filter(user=self.normal_user, club=self.club).count(),1
        )
        
        # Send a deletion request
        response = self.client.post(
            reverse('admin_panel_remove_memberships', args=[self.normal_user.username, self.club.pk])
        )
        
        # Check for redirection to user's membership page
        self.assertRedirects(
            response, 
            reverse('admin_panel_user_memberships', args=[self.normal_user.username])
        )
        
        # Check if the membership has been deleted
        self.assertEqual(
            Membership.objects.filter(user=self.normal_user, club=self.club).count(),0
        )

    def test_admin_panel_new_club_requests_view(self):
        """Test admin panel new club request list view"""
        self.client.login(username='@adminuser', password='adminpass123')
        
        # Creating a test new club request
        pending_request = NewClubRequest.objects.create(
            name="Pending Test Club",
            description="Pending Test Club Description",
            creator=self.normal_user,
            status='pending'
        )
        
        response = self.client.get(reverse('admin_panel_new_club_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_requests/new_club_requests.html')
        
        self.assertEqual(response.context['pending_count'], 1)
        self.assertEqual(list(response.context['pending_ncRequests']), [pending_request])
        
        # Testing the Search Function - Searching for Existing Requests
        response = self.client.get(reverse('admin_panel_new_club_requests'), {'search': 'Pending'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pending_count'], 1)
        self.assertEqual(list(response.context['pending_ncRequests']), [pending_request])
        
        pending_request.delete()

    def test_admin_panel_new_club_request_detail_view(self):
        """Test Administrator Panel New Club Request Detail View"""

        self.client.login(username='@adminuser', password='adminpass123')
        
        # Creating a test new club request
        test_request = NewClubRequest.objects.create(
            name="Test Detail Club",
            description="Test Detail Club Description",
            creator=self.normal_user,
            status='pending'
        )
        
        response = self.client.get(reverse('admin_panel_new_club_requests_detail', args=[test_request.request_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_requests/new_club_request_detail.html')
        
        self.assertEqual(response.context['ncRequest'], test_request)
        self.assertEqual(response.context['creator'], self.normal_user)
        
        test_request.delete()

    def test_admin_review_new_club_request_view(self):
        """Test administrator review of new club request view"""

        self.client.login(username='@adminuser', password='adminpass123')
        
        # Creating a test new club request
        test_request = NewClubRequest.objects.create(
            name="Test Review Club",
            description="Test Review Club Description",
            creator=self.normal_user,
            status='pending'
        )
        
        # Testing GET Requests
        response = self.client.get(reverse('admin_review_new_club_request', args=[test_request.request_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_requests/new_club_request_detail.html')

        self.assertEqual(response.context['ncRequest'], test_request)
        
        # Testing POST Requests - Accepting Club Requests
        response = self.client.post(
            reverse('admin_review_new_club_request', args=[test_request.request_id]),
            {
                'action': 'accept',
                'review': 'This is a good club idea.'
            }
        )
        
        self.assertRedirects(response, reverse('admin_panel_new_club_requests'))
        test_request.refresh_from_db()
        
        # Check if the request status has been updated to approved
        self.assertEqual(test_request.status, NewClubRequest.STATUS_APPROVED)
        self.assertEqual(test_request.review, 'This is a good club idea.')
        self.assertEqual(test_request.reviewed_by, self.admin_user)
        
        # Check if a new club has been created
        self.assertTrue(Club.objects.filter(name="Test Review Club").exists())
        new_club = Club.objects.get(name="Test Review Club")
        
        # Check if a membership has been created
        self.assertTrue(Membership.objects.filter(user=self.normal_user, club=new_club, is_manager=True).exists())
        
        # Create another test request to test the rejection feature
        reject_request = NewClubRequest.objects.create(
            name="Test Reject Club",
            description="Test Reject Club Description",
            creator=self.normal_user,
            status='pending'
        )
        
        # Testing POST Requests - Rejecting Club Requests
        response = self.client.post(
            reverse('admin_review_new_club_request', args=[reject_request.request_id]),
            {
                'action': 'reject',
                'review': 'This club idea is not suitable.'
            }
        )
        
        self.assertRedirects(response, reverse('admin_panel_new_club_requests'))
        reject_request.refresh_from_db()
        
        # Check if the request status has been updated to rejected
        self.assertEqual(reject_request.status, NewClubRequest.STATUS_REJECTED)
        self.assertEqual(reject_request.review, 'This club idea is not suitable.')
        self.assertEqual(reject_request.reviewed_by, self.admin_user)
        
        new_club.delete()
        test_request.delete()
        reject_request.delete()