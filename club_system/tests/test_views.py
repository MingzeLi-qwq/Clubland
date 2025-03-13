from django.test import TestCase, Client
from django.urls import reverse
from club_system.models import Club, Membership, NewClubRequest
from user_system.models import User
from event_system.models import Event
from django.utils import timezone
from club_system.views import isSameClubNameExist, isSameClubNameExistInRequest

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
        
        self.user2 = User.objects.create_user(
            username="@testuse2r",
            email="test2@example.com",
            password="testpass123",
            first_name="Testtwo",
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

        self.user2_membership = Membership.objects.create(
            user=self.user2,
            club=self.club,
        )

        # 创建测试俱乐部申请
        self.club_request = NewClubRequest.objects.create(
            creator=self.user,
            name="New Test Club",
            description="New Test Description",
            status=NewClubRequest.STATUS_PENDING
        )
        

    def test_clubs_list_view(self):
        """测试俱乐部列表视图"""
        response = self.client.get(reverse('clubs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        
        # 测试搜索功能
        response = self.client.get(reverse('clubs'), {'search': 'Test'})
        self.assertContains(response, 'Test Club')
        
    def test_isSameClubNameExist(self):
        """测试 isSameClubNameExist 函数是否能正确检测重复的俱乐部名称"""
        # 测试完全相同的名称
        self.assertTrue(isSameClubNameExist("Test Club"))
        
        # 测试不同的名称
        self.assertFalse(isSameClubNameExist("Different Club"))
        
        # 测试忽略大小写
        self.assertTrue(isSameClubNameExist("TEST CLUB"))
        self.assertTrue(isSameClubNameExist("test club"))
        
        # 测试忽略空格
        self.assertTrue(isSameClubNameExist("TestClub"))
        self.assertTrue(isSameClubNameExist("Test  Club"))
        self.assertTrue(isSameClubNameExist(" Test Club "))
        
        # 测试同时忽略大小写和空格
        self.assertTrue(isSameClubNameExist("TESTCLUB"))
        self.assertTrue(isSameClubNameExist("test  club"))
        

    def test_isSameClubNameExistInRequest(self):
        """测试 isSameClubNameExistInRequest 函数是否能正确检测重复的俱乐部申请名称"""
        # 测试完全相同的名称
        self.assertTrue(isSameClubNameExistInRequest("New Test Club"))
        
        # 测试不同的名称
        self.assertFalse(isSameClubNameExistInRequest("Different Club Request"))
        
        # 测试忽略大小写
        self.assertTrue(isSameClubNameExistInRequest("NEW TEST CLUB"))
        self.assertTrue(isSameClubNameExistInRequest("new test club"))
        
        # 测试忽略空格
        self.assertTrue(isSameClubNameExistInRequest("NewTestClub"))
        self.assertTrue(isSameClubNameExistInRequest("New  Test  Club"))
        self.assertTrue(isSameClubNameExistInRequest(" New Test Club "))
        
        # 测试同时忽略大小写和空格
        self.assertTrue(isSameClubNameExistInRequest("NEWTESTCLUB"))
        self.assertTrue(isSameClubNameExistInRequest("new  test  club"))


    def test_club_manager_members_view(self):
        """测试俱乐部管理员成员页面视图"""
        # 登录管理员用户
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 访问成员管理页面
        response = self.client.get(reverse('club_manager_members', args=[self.club.pk]))
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查使用的模板
        self.assertTemplateUsed(response, 'club_manager/members.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['manager_count'], 1)  # 只有一个管理员
        self.assertEqual(response.context['muggle_count'], 1)   # 只有一个普通成员
        
    def test_club_manager_members_search(self):
        """测试俱乐部管理员成员页面的搜索功能"""
        # 登录管理员用户
        self.client.login(username='@manageruser', password='managerpass123')

        # 测试管理员搜索
        response = self.client.get(
            reverse('club_manager_members', args=[self.club.pk]),
            {'manager_search': 'Manager'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'manager@example.com')
        
        # 测试成员搜索
        response = self.client.get(
            reverse('club_manager_members', args=[self.club.pk]),
            {'member_search': 'Testtwo'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test2@example.com')
        
        # 测试邮箱搜索
        response = self.client.get(
            reverse('club_manager_members', args=[self.club.pk]),
            {'member_search': 'test2@example.com'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Testtwo')
        
        # 测试无结果搜索
        response = self.client.get(
            reverse('club_manager_members', args=[self.club.pk]),
            {'member_search': 'NonExistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'test2@example.com')
        
    
    @classmethod
    def tearDownClass(cls):
        """在所有测试完成后执行全局清理（仅执行一次）"""
        super().tearDownClass()
        User.objects.all().delete()
        Club.objects.all().delete()
        Membership.objects.all().delete()
        NewClubRequest.objects.all().delete()