from django.test import TestCase, Client
from django.urls import reverse
from club_system.models import Club, Membership
from user_system.models import User
from django.utils import timezone

class ClubSystemMixinsTest(TestCase):
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
        
        # 创建管理员用户
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
        
        # 创建一个不存在的club_id
        self.non_existent_club_id = 9999  # 假设这个ID不存在
    
    # def test_club_member_required_mixin(self):
    #     """测试 ClubMemberRequiredMixin - 权限验证"""
    #     # 测试未授权访问
    #     self.client.login(username='@testuser', password='testpass123')
    #     response = self.client.get(reverse('club_web', args=[self.club.pk]))
    #     self.assertEqual(response.status_code, 403)  # 明确状态码断言
    #     self.assertIn("not a member", response.content.decode())
    
    #     # 测试授权访问
    #     Membership.objects.create(user=self.user, club=self.club)
    #     response = self.client.get(reverse('club_web', args=[self.club.pk])) 
    #     self.assertEqual(response.status_code, 200)  # 通过不会重定向的视图验证
    
    #     # 测试未登录访问
    #     self.client.logout()
    #     response = self.client.get(reverse('club_web', args=[self.club.pk]))
    #     self.assertEqual(response.status_code, 302)  # 验证登录重定向
    
    def test_club_manager_required_mixin_non_member(self):
        """测试 ClubManagerRequiredMixin - 非社团成员访问 club manager 会被拒绝"""
        # 尝试访问需要管理员权限的页面（例如：club_manager_general）
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('club_manager_general', args=[self.club.pk]))
        
        # 由于用户不是管理员，应该被拒绝访问
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("You are not an administrator", response.content.decode())
    
    def test_club_manager_required_mixin_non_manager(self):
        """测试 ClubManagerRequiredMixin - 非社团管理员(但是社团成员)访问 club manager 会被拒绝"""
        # 创建会员关系（非管理员）
        Membership.objects.create(user=self.user, club=self.club)
        
        # 尝试访问需要管理员权限的页面
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('club_manager_general', args=[self.club.pk]))
        
        # 由于用户不是管理员，应该被拒绝访问
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("You are not an administrator", response.content.decode())
        
        # 使用管理员账户登录
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.get(reverse('club_manager_general', args=[self.club.pk]))
        
        # 现在用户是管理员，应该可以访问
        self.assertEqual(response.status_code, 200)
    
    def test_club_manager_required_mixin_admin_override(self):
        """测试 ClubManagerRequiredMixin - 系统管理员可以访问 club manager 页面"""
        # 使用系统管理员账户登录
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.get(reverse('club_manager_general', args=[self.club.pk]))
        
        # 系统管理员应该可以访问，即使不是俱乐部成员
        self.assertEqual(response.status_code, 200)
    
    def test_non_club_manager_required_mixin(self):
        """测试 NonClubManagerRequiredMixin - 社团管理员访问取消会员方法会被拒绝"""
        # 创建会员关系
        Membership.objects.create(user=self.user, club=self.club)
        
        # 使用普通会员账户登录
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('cancel_membership', args=[self.club.pk]))
        
        # 普通会员应该可以访问取消会员页面
        self.assertRedirects(response, reverse('dashboard_my_club'))
        
        # 使用管理员账户登录
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.get(reverse('cancel_membership', args=[self.club.pk]))
        
        # 管理员应该被拒绝访问取消会员页面
        self.assertNotEqual(response.status_code, 302)  # 不应该重定向
        self.assertIn("You are the club administrator", response.content.decode())
    
    def test_non_club_member_required_mixin(self):
        """测试 NonClubMemberRequiredMixin - 社团成员访问注册会员的方法会被拒绝"""
        # 创建会员关系
        Membership.objects.create(user=self.user, club=self.club)
        
        # 使用已是会员的账户登录
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(reverse('register_membership', args=[self.club.pk]))
        
        # 已是会员的用户应该被拒绝访问注册会员页面
        self.assertNotEqual(response.status_code, 302)  # 不应该重定向
        self.assertIn("You are already a member", response.content.decode())
        
        # 创建一个新用户（非会员）
        non_member = User.objects.create_user(
            username="@nonmember",
            email="nonmember@example.com",
            password="nonmemberpass123",
            account_type="User"
        )
        
        # 使用非会员账户登录
        self.client.login(username='@nonmember', password='nonmemberpass123')
        response = self.client.get(reverse('register_membership', args=[self.club.pk]))
        
        # 非会员应该可以访问注册会员页面
        self.assertRedirects(response, reverse('club_detail', args=[self.club.pk]))
    
    def test_club_exists_required_mixin(self):
        """测试 ClubExistsRequiredMixin - 试图访问一个不存在的club的详情页会被拒绝"""
        # 尝试访问不存在的俱乐部详情页
        response = self.client.get(reverse('club_detail', args=[self.non_existent_club_id]))
        
        # 应该被拒绝访问
        self.assertNotEqual(response.status_code, 200)
        self.assertIn("The club does not exist", response.content.decode())
        
        # 访问存在的俱乐部详情页
        response = self.client.get(reverse('club_detail', args=[self.club.pk]))
        
        # 应该可以正常访问
        self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        """清理测试数据"""
        User.objects.all().delete()
        Club.objects.all().delete()
        Membership.objects.all().delete()
