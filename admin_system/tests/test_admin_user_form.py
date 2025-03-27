from django.test import TestCase, Client
from django.urls import reverse
from user_system.models import User
from django.db import IntegrityError
from django.contrib.messages import get_messages

class AdminPanelAdminUsersTests(TestCase):
    def setUp(self):
        # Create an administrator user for logging in
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='Admin',
            account_type=User.ACCOUNT_TYPE_ADMIN
        )
        
        # Create some general administrator users for testing the list display
        for i in range(3):
            User.objects.create_user(
                username=f'admin{i}',
                email=f'admin{i}@example.com',
                password='password123',
                first_name=f'Admin{i}',
                last_name='User',
                account_type=User.ACCOUNT_TYPE_ADMIN
            )
    
        self.client = Client()
        self.client.login(username='testadmin', password='testpassword123')

        self.admin_users_url = reverse('admin_panel_admin_users')
    
    def test_admin_users_page_access(self):
        """Test access to the administrator user list page"""
        response = self.client.get(self.admin_users_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_users.html')
        
        self.assertIn('admin_users', response.context)
        self.assertIn('admin_user_count', response.context)
        self.assertEqual(response.context['admin_user_count'], 4)

    def tearDown(self):
        """Cleaning up test data"""
        User.objects.all().delete()
        self.client.logout()