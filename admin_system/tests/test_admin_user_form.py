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

    def test_admin_users_search(self):
        """Test the admin user search function"""
        # Test Search by Name
        response = self.client.get(f"{self.admin_users_url}?search=Admin0")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['admin_users']), 1)
        
        # Test Search by Email
        response = self.client.get(f"{self.admin_users_url}?search=admin1@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['admin_users']), 1)

    def test_create_admin_user_success(self):
        """Test successful creation of administrator user"""
        new_admin_data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        
        response = self.client.post(self.admin_users_url, new_admin_data, follow=True)
        
        self.assertRedirects(response, self.admin_users_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('created successfully', str(messages[0]))
        
        # Verify that the user has been created
        self.assertTrue(User.objects.filter(username='newadmin').exists())
        new_user = User.objects.get(username='newadmin')
        self.assertEqual(new_user.account_type, User.ACCOUNT_TYPE_ADMIN)

    def tearDown(self):
        """Cleaning up test data"""
        User.objects.all().delete()
        self.client.logout()