from django.test import TestCase, Client
from django.urls import reverse
from club_system.models import Club, Membership, NewClubRequest
from user_system.models import User
from event_system.models import Event
from django.utils import timezone

class ClubSystemViewsTest(TestCase):
    def setUp(self):
        # 创建测试客户端
        self.client = Client()
        
        # 创建普通测试用户
        self.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            account_type="User"
        )
        
        # 创建管理员用户（不与club建立会员关系）
        self.admin_user = User.objects.create_user(
            username="@adminuser",
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            account_type="Admin"
        )
        
        # 创建另一个普通用户作为club manager
        self.manager_user = User.objects.create_user(
            username="@manageruser",
            email="manager@example.com",
            password="managerpass123",
            first_name="Manager",
            last_name="User",
            account_type="User"
        )
        
        # 创建测试俱乐部
        self.club = Club.objects.create(
            name="Test Club",
            description="Test Description"
        )
        
        # 创建普通用户作为manager的会员关系
        self.manager_membership = Membership.objects.create(
            user=self.manager_user,
            club=self.club,
            is_manager=True
        )

    def test_clubs_list_view(self):
        """测试俱乐部列表视图"""
        response = self.client.get(reverse('clubs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        
        # 测试搜索功能
        response = self.client.get(reverse('clubs'), {'search': 'Test'})
        self.assertContains(response, 'Test Club')

    def test_club_detail_view(self):
        """测试俱乐部详情视图"""
        response = self.client.get(reverse('club_detail', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_detail.html')

    def test_register_membership(self):
        """测试注册会员功能"""
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('register_membership', args=[self.club.pk]))
        self.assertRedirects(response, reverse('club_detail', args=[self.club.pk]))
        
        # 验证会员关系是否创建
        self.assertTrue(Membership.objects.filter(user=self.user, club=self.club).exists())

    def test_cancel_membership(self):
        """测试取消会员功能"""
        # 先创建会员关系
        Membership.objects.create(user=self.user, club=self.club)
        
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('cancel_membership', args=[self.club.pk]))
        self.assertRedirects(response, reverse('dashboard_my_club'))
        
        # 验证会员关系是否删除
        self.assertFalse(Membership.objects.filter(user=self.user, club=self.club).exists())

    def test_club_manager_functions(self):
        """测试俱乐部管理功能"""
        # 使用普通用户作为manager登录
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 测试更新俱乐部名称
        new_name = "Updated Test Club"
        response = self.client.post(reverse('update_club_name', args=[self.club.pk]), {
            'club_name': new_name
        })
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, new_name)
        
        # 测试更新俱乐部描述
        new_description = "Updated Description"
        response = self.client.post(reverse('update_club_description', args=[self.club.pk]), {
            'club_description': new_description
        })
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, new_description)

    # def test_admin_access(self):
    #     """测试管理员访问权限"""
    #     self.client.login(username='@adminuser', password='adminpass123')
        
    #     # 管理员应该能访问俱乐部管理页面，即使没有会员关系
    #     response = self.client.get(reverse('admin_panel_clubs'))
    #     self.assertEqual(response.status_code, 200)

    def test_new_club_request(self):
        """测试新俱乐部申请功能"""
        self.client.login(username='@testuser', password='testpass123')
        
        response = self.client.post(reverse('apply_new_club'), {
            'name': 'New Test Club',
            'description': 'New Club Description'
        })
        
        # 验证是否创建了新的申请
        self.assertTrue(NewClubRequest.objects.filter(name='New Test Club').exists())

    def test_search_users(self):
        """测试用户搜索功能"""
        self.client.login(username='@manageruser', password='managerpass123')
        
        response = self.client.get(reverse('search_users'), {
            'q': 'test',
            'club_id': self.club.pk
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('testuser', response.content.decode())

    def test_add_member(self):
        """测试添加会员功能"""
        # 创建一个新用户
        new_user = User.objects.create_user(
            username="@newuser",
            email="new@example.com",
            password="newpass123",
            first_name="New",
            last_name="User",
            account_type="User"
        )
        
        # 使用manager用户登录
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 添加新会员
        response = self.client.post(reverse('add_member', args=[self.club.pk, new_user.username]))
        
        # 验证会员关系是否创建
        self.assertTrue(Membership.objects.filter(user=new_user, club=self.club).exists())

    def test_remove_member(self):
        """测试移除会员功能"""
        # 创建一个新用户并添加为会员
        new_user = User.objects.create_user(
            username="@memberuser",
            email="member@example.com",
            password="memberpass123",
            first_name="Member",
            last_name="User",
            account_type="User"
        )
        
        Membership.objects.create(user=new_user, club=self.club)
        
        # 使用manager用户登录
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 移除会员
        response = self.client.post(reverse('remove_member', args=[self.club.pk, new_user.username]))
        
        # 验证会员关系是否删除
        self.assertFalse(Membership.objects.filter(user=new_user, club=self.club).exists())

    def tearDown(self):
        """清理测试数据"""
        User.objects.all().delete()
        Club.objects.all().delete()
        Membership.objects.all().delete()
        NewClubRequest.objects.all().delete()