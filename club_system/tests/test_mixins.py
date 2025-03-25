from django.test import TestCase, Client
from django.urls import reverse
from club_system.models import Club, Membership
from user_system.models import User
from django.utils import timezone

class ClubSystemMixinsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Creating a Normal Test User
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            account_type="User"
        )
        
        # Creating an Administrator User
        self.admin_user = User.objects.create_user(
            username="@adminuser",
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            account_type="Admin"
        )
        
        # Create another normal user as club manager
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
        
        # Create a membership relationship with a regular user as a manager
        self.manager_membership = Membership.objects.create(
            user=self.manager_user,
            club=self.club,
            is_manager=True
        )
        
        # Create a club id that does not exist
        self.non_existent_club_id = 9999
    

    def test_club_manager_required_mixin_non_member(self):
        """Test ClubManagerRequiredMixin - Non-member members will be denied access to club manager"""
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('club_manager_general', args=[self.club.pk]))
        
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("You are not an administrator", response.content.decode())
    
    def test_club_manager_required_mixin_non_manager(self):
        """Test ClubManagerRequiredMixin - access to club manager by non-club administrators (but club members) is denied"""
        Membership.objects.create(user=self.user, club=self.club)
        
        # Trying to access a page that requires administrator privileges - Access denied
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('club_manager_general', args=[self.club.pk]))
        
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("You are not an administrator", response.content.decode())
        
        # Log in with an administrator account - you can access
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.get(reverse('club_manager_general', args=[self.club.pk]))
        
        self.assertEqual(response.status_code, 200)
    
    def test_club_manager_required_mixin_admin_override(self):
        """Test ClubManagerRequiredMixin - system administrator has access to club manager page"""
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.get(reverse('club_manager_general', args=[self.club.pk]))

        self.assertEqual(response.status_code, 200)
    
    def test_non_club_manager_required_mixin(self):
        """测试 NonClubManagerRequiredMixin - 社团管理员访问取消会员方法会被拒绝"""
        Membership.objects.create(user=self.user, club=self.club)
        
        # Log in with a regular member account - you can access
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('cancel_membership', args=[self.club.pk]))
        
        self.assertRedirects(response, reverse('dashboard_my_club'))
        
        # Login with administrator account - Access denied
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.get(reverse('cancel_membership', args=[self.club.pk]))
        
        self.assertNotEqual(response.status_code, 302)  
        self.assertIn("You are the club administrator", response.content.decode())
    
    def test_non_club_member_required_mixin(self):
        """Test NonClubMemberRequiredMixin - club member access to registered members is denied"""
        Membership.objects.create(user=self.user, club=self.club)
        
        # Login with an account that is already a member - Login with an account that is already a member
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('register_membership', args=[self.club.pk]))
        
        self.assertNotEqual(response.status_code, 302)  
        self.assertIn("You are already a member", response.content.decode())
        
        # Create a new user (non-member)
        non_member = User.objects.create_user(
            username="@nonmember",
            email="nonmember@example.com",
            password="nonmemberpass123",
            account_type="User"
        )
        
        self.client.login(username='@nonmember', password='nonmemberpass123')
        response = self.client.get(reverse('register_membership', args=[self.club.pk]))
        
        # Non-members should be able to access the registered member page
        self.assertRedirects(response, reverse('club_detail', args=[self.club.pk]))
    
    def test_club_exists_required_mixin(self):
        """Test ClubExistsRequiredMixin - Attempts to access the details page of a non-existent club are denied!"""
        # Trying to access a club detail page that doesn't exist - Denial of access
        response = self.client.get(reverse('club_detail', args=[self.non_existent_club_id]))
        
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("The club does not exist", response.content.decode())
        
        # Access to existent club details page - access allowed
        response = self.client.get(reverse('club_detail', args=[self.club.pk]))
        
        self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        """Cleaning up test data"""
        User.objects.all().delete()
        Club.objects.all().delete()
        Membership.objects.all().delete()
