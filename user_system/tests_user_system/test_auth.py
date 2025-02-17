from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class UserAuthTests(TestCase):

    def setUp(self):
        """Make sure the user is not in the database before testing"""
        User.objects.filter(username="@testuser").delete()
        User.objects.filter(email="test@example.com").delete()
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            account_type="User",
            password="TestPassword123!"
        )
    
    def test_signup_view(self):
        """Test user registration"""
        response = self.client.post(reverse('signup'), {
            'username': '@newuser',
            'email': 'newuser@example.com',
            'first_name': 'new',
            'last_name': 'user',
            'account_type': 'User',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="@newuser").exists())

    def test_login_view(self):
        """Test user login"""
        response = self.client.post(reverse('login'), {
            'username': '@testuser',
            'password': 'TestPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_view(self):
        """Test user logout"""
        self.client.login(username="@testuser", password="TestPassword123!")
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('home'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have successfully logged out.")

    def test_invalid_login(self):
        """Test the wrong login information"""
        response = self.client.post(reverse('login'), {
            'username': '@testuser',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_change_password(self):
        """测试用户修改密码"""
        self.client.login(username="@testuser", password="TestPassword123!")
        
        # 发送修改密码请求
        response = self.client.post(reverse('change_password'), {
            'old_password': 'TestPassword123!',
            'new_password1': 'NewTestPassword456!',
            'new_password2': 'NewTestPassword456!',
        })
        self.assertEqual(response.status_code, 302) 
        
        '''旧密码无法登录'''
        self.client.logout()
        login_failed = self.client.login(username="@testuser", password="TestPassword123!")
        self.assertFalse(login_failed)

        '''新密码可以登录'''
        login_success = self.client.login(username="@testuser", password="NewTestPassword456!")
        self.assertTrue(login_success)
