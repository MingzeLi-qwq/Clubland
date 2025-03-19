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

        # 创建两个测试用的event
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


    def test_club_manager_events_view(self):
        """测试俱乐部管理员事件页面视图"""
        # 登录管理员用户
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 访问事件管理页面
        response = self.client.get(reverse('club_manager_events', args=[self.club.pk]))
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查使用的模板
        self.assertTemplateUsed(response, 'club_manager/events.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(response.context['club'], self.club)
        
        # 检查事件列表是否包含两个测试事件
        self.assertEqual(len(response.context['events']), 2)
        self.assertContains(response, 'Test Event 1')
        self.assertContains(response, 'Special Workshop')
        
    def test_club_manager_events_search(self):
        """测试俱乐部管理员事件页面的搜索功能"""
        # 登录管理员用户
        self.client.login(username='@manageruser', password='managerpass123')

        # 测试事件名称搜索
        response = self.client.get(
            reverse('club_manager_events', args=[self.club.pk]),
            {'search': 'Special'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Special Workshop')
        self.assertNotContains(response, 'Test Event 1')
        
        # 测试日期搜索
        tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse('club_manager_events', args=[self.club.pk]),
            {'search': tomorrow}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event 1')
        self.assertNotContains(response, 'Special Workshop')
        
        # 测试无结果搜索
        response = self.client.get(
            reverse('club_manager_events', args=[self.club.pk]),
            {'search': 'NonExistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Event 1')
        self.assertNotContains(response, 'Special Workshop')

    
    def test_update_club_name(self):
        """测试更新俱乐部名称功能"""
        # 创建另一个俱乐部用于测试名称重复
        club2 = Club.objects.create(
            name="Test Club 2",
            description="Test Description 2"
        )
        
        # 测试管理员用户 - 新名字不能与旧名字重复
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'Test Club'}
        )
        self.assertEqual(self.club.name, "Test Club")  # 名称应该保持不变
        
        # 测试俱乐部管理员 - 新名字不能为空
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': ''}
        )
        self.assertEqual(self.club.name, "Test Club")  # 名称应该保持不变
        
        # 测试俱乐部管理员 - 新名字不能与现有俱乐部名称重复
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'Test Club 2'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "Test Club")  # 名称应该保持不变
        
        # 测试俱乐部管理员 - 新名字不能与待审核的请求名称重复
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'New Test Club'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "Test Club")  # 名称应该保持不变
        
        # 测试俱乐部管理员 - 成功更新名称
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'New Test Club Name'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "New Test Club Name")  # 名称应该已更新
        
        # 测试俱乐部管理员 - 将名称改回原来的名称
        response = self.client.post(
            reverse('update_club_name', args=[self.club.pk]),
            {'club_name': 'Test Club'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "Test Club")  # 名称应该已改回
        
        # 清理测试数据
        club2.delete()
        
    def test_update_club_description(self):
        """测试更新俱乐部描述功能"""
        # 测试管理员用户 - 新描述不能与旧描述重复
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('update_club_description', args=[self.club.pk]),
            {'club_description': 'Test Description'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, "Test Description")  # 描述应该保持不变
        
        # 测试俱乐部管理员 - 新描述不能与旧描述重复
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.post(
            reverse('update_club_description', args=[self.club.pk]),
            {'club_description': 'Test Description'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, "Test Description")  # 描述应该保持不变
        
        # 测试俱乐部管理员 - 新描述为空会使用默认描述
        response = self.client.post(
            reverse('update_club_description', args=[self.club.pk]),
            {'club_description': ''}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, "This Club hasn't added a Description yet")  # 描述应该更新为默认值
        
        # 测试俱乐部管理员 - 成功更新描述
        response = self.client.post(
            reverse('update_club_description', args=[self.club.pk]),
            {'club_description': 'New Test Club Description'}
        )
        self.club.refresh_from_db()
        self.assertEqual(self.club.description, "New Test Club Description")  # 描述应该已更新

    def test_remove_manager(self):
        """测试移除俱乐部管理员功能"""
        # 创建另一个管理员用户，以便测试移除管理员后仍有管理员存在
        another_manager = User.objects.create_user(
            username="@anothermanager",
            email="another@example.com",
            password="managerpass123",
            first_name="Another",
            last_name="Manager",
            account_type="User"
        )
        
        # 将该用户设为管理员
        another_manager_membership = Membership.objects.create(
            user=another_manager,
            club=self.club,
            is_manager=True
        )
        
        # 测试管理员用户移除管理员
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('remove_manager', args=[self.club.pk, '@manageruser'])
        )
        
        # 检查管理员是否被移除
        membership = Membership.objects.get(user=self.manager_user, club=self.club)
        self.assertFalse(membership.is_manager)
        
        # 恢复管理员身份用于后续测试
        membership.is_manager = True
        membership.save()
        
        # 测试俱乐部管理员移除另一个管理员
        self.client.login(username='@manageruser', password='managerpass123')
        response = self.client.post(
            reverse('remove_manager', args=[self.club.pk, '@anothermanager'])
        )
        
        # 检查另一个管理员是否被移除
        another_membership = Membership.objects.get(user=another_manager, club=self.club)
        self.assertFalse(another_membership.is_manager)
        
        # 测试移除最后一个管理员（应该失败）
        response = self.client.post(
            reverse('remove_manager', args=[self.club.pk, '@manageruser'])
        )
        
        # 检查管理员是否仍然存在（不应被移除）
        membership = Membership.objects.get(user=self.manager_user, club=self.club)
        self.assertTrue(membership.is_manager)
        
        # 清理测试数据
        another_manager_membership.delete()
        another_manager.delete()

    def test_set_manager_view(self):
        """测试设置俱乐部管理员功能"""
        # 创建一个普通成员用于测试设置为管理员
        normal_member = User.objects.create_user(
            username="@normalmember",
            email="normal@example.com",
            password="testpass123",
            first_name="Normal",
            last_name="Member",
            account_type="User"
        )
        
        # 创建会员关系（非管理员）
        normal_membership = Membership.objects.create(
            user=normal_member,
            club=self.club,
            is_manager=False
        )
        
        # 登录管理员用户
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 测试将普通成员设置为管理员
        response = self.client.post(
            reverse('set_manager', args=[self.club.pk, '@normalmember'])
        )
        normal_membership.refresh_from_db()
        self.assertTrue(normal_membership.is_manager)  # 应该已被设置为管理员
        
        # 测试将已是管理员的成员再次设置为管理员
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('set_manager', args=[self.club.pk, '@normalmember'])
        )
        normal_membership.refresh_from_db()
        self.assertTrue(normal_membership.is_manager)  # 管理员状态应保持不变
        
        # 清理测试数据
        normal_member.delete()

    def test_remove_member_view(self):
        """测试移除俱乐部普通成员功能"""
        # 创建一个普通成员用于测试移除
        normal_member = User.objects.create_user(
            username="@normalmember",
            email="normal@example.com",
            password="testpass123",
            first_name="Normal",
            last_name="Member",
            account_type="User"
        )
        
        # 创建会员关系（非管理员）
        normal_membership = Membership.objects.create(
            user=normal_member,
            club=self.club,
            is_manager=False
        )
        
        # 登录管理员用户
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 测试移除不存在的用户
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@nonexistentuser'])
        )
        # 检查会员数量是否保持不变
        self.assertEqual(Membership.objects.filter(club=self.club).count(), 3)  # 原有2个 + 新增1个
        
        # 测试移除不属于该俱乐部的用户
        another_user = User.objects.create_user(
            username="@anotheruser",
            email="another@example.com",
            password="testpass123",
            first_name="Another",
            last_name="User",
            account_type="User"
        )
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@anotheruser'])
        )
        # 检查会员数量是否保持不变
        self.assertEqual(Membership.objects.filter(club=self.club).count(), 3)
        
        # 测试移除管理员（应该失败）
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@manageruser'])
        )
        # 检查管理员是否仍然存在
        self.assertTrue(Membership.objects.filter(user=self.manager_user, club=self.club).exists())
        
        # 测试成功移除普通成员
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@normalmember'])
        )
        # 检查普通成员是否已被移除
        self.assertFalse(Membership.objects.filter(user=normal_member, club=self.club).exists())
        
        # 测试管理员用户移除成员
        # 先重新创建会员关系
        normal_membership = Membership.objects.create(
            user=normal_member,
            club=self.club,
            is_manager=False
        )
        self.client.login(username='@adminuser', password='adminpass123')
        response = self.client.post(
            reverse('remove_member', args=[self.club.pk, '@normalmember'])
        )
        # 检查普通成员是否已被移除
        self.assertFalse(Membership.objects.filter(user=normal_member, club=self.club).exists())
        
        # 清理测试数据
        normal_member.delete()
        another_user.delete()

    def test_club_manager_event_general_view(self):
        """测试俱乐部管理员事件一般信息页面视图"""
        # 登录管理员用户
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 访问事件一般信息管理页面
        response = self.client.get(
            reverse('club_manager_event_general', args=[self.club.pk, self.event1.pk])
        )
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查使用的模板
        self.assertTemplateUsed(response, 'club_manager/event/general.html')
        
        # 测试非管理员用户访问（应该被重定向）
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(
            reverse('club_manager_event_general', args=[self.club.pk, self.event1.pk])
        )
        self.assertNotEqual(response.status_code, 200)  # 应该不是200，可能是302重定向

    def test_club_manager_event_rsvps_view(self):
        """测试俱乐部管理员事件RSVP列表页面视图"""
        # 创建一个RSVP记录用于测试
        rsvp = RSVP.objects.create(
            user=self.user,
            event=self.event1
        )
        
        # 登录管理员用户
        self.client.login(username='@manageruser', password='managerpass123')
        
        # 访问事件RSVP管理页面
        response = self.client.get(
            reverse('club_manager_event_RSVPs', args=[self.club.pk, self.event1.pk])
        )
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查使用的模板
        self.assertTemplateUsed(response, 'club_manager/event/RSVPs.html')
        
        # 测试搜索功能
        response = self.client.get(
            reverse('club_manager_event_RSVPs', args=[self.club.pk, self.event1.pk]),
            {'search': 'Test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rsvps']), 1)  # 应该找到一个结果
        
        # 测试无结果搜索
        response = self.client.get(
            reverse('club_manager_event_RSVPs', args=[self.club.pk, self.event1.pk]),
            {'search': 'NonExistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rsvps']), 0)  # 应该没有结果
        
        # 测试非管理员用户访问（应该被重定向）
        self.client.login(username='@testuser', password='testpass123')
        response = self.client.get(
            reverse('club_manager_event_RSVPs', args=[self.club.pk, self.event1.pk])
        )
        self.assertNotEqual(response.status_code, 200)  # 应该不是200，可能是302重定向
        
        # 清理测试数据
        rsvp.delete()

    def test_apply_new_club_view_get(self):
        """测试申请新俱乐部页面的GET请求"""
        # 登录普通用户
        self.client.login(username='@testuser', password='testpass123')
        
        # 访问申请新俱乐部页面
        response = self.client.get(reverse('apply_new_club'))
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查使用的模板
        self.assertTemplateUsed(response, 'apply_new_club.html')
        
        # 检查表单是否在上下文中
        self.assertTrue('form' in response.context)
        
        # 测试未登录用户访问（应该被重定向）
        self.client.logout()
        response = self.client.get(reverse('apply_new_club'))
        self.assertNotEqual(response.status_code, 200)  # 应该不是200，可能是302重定向

    def test_apply_new_club_view_post(self):
        """测试申请新俱乐部页面的POST请求"""
        # 登录普通用户
        self.client.login(username='@testuser', password='testpass123')
        
        # 测试提交有效表单
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': 'Brand New Club',
                'description': 'This is a brand new club for testing'
            }
        )
        
        # 检查是否创建了新的俱乐部申请
        self.assertTrue(NewClubRequest.objects.filter(name='Brand New Club').exists())
        new_request = NewClubRequest.objects.get(name='Brand New Club')
        self.assertEqual(new_request.creator, self.user)
        self.assertEqual(new_request.description, 'This is a brand new club for testing')
        self.assertEqual(new_request.status, NewClubRequest.STATUS_PENDING)
        
        # 测试提交与现有俱乐部重名的表单
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': 'Test Club',  # 与已存在的俱乐部同名
                'description': 'This should fail'
            }
        )
        
        # 检查是否返回错误信息
        self.assertEqual(response.status_code, 200)  # 应该返回表单页面
        self.assertContains(response, "A club with this name already exists")
        
        # 测试提交与待审核请求重名的表单
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': 'New Test Club',  # 与已存在的申请同名
                'description': 'This should also fail'
            }
        )
        
        # 检查是否返回表单错误
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['form'].errors)
        
        # 测试提交空名称的表单
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': '',
                'description': 'This should fail due to empty name'
            }
        )
        
        # 检查是否返回表单错误
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['form'].errors)
        
        # 测试未登录用户提交（应该被重定向）
        self.client.logout()
        response = self.client.post(
            reverse('apply_new_club'),
            {
                'name': 'Another New Club',
                'description': 'This should fail due to not logged in'
            }
        )
        self.assertNotEqual(response.status_code, 200)  # 应该不是200，可能是302重定向
        
        # 检查是否没有创建新的俱乐部申请
        self.assertFalse(NewClubRequest.objects.filter(name='Another New Club').exists())

    @classmethod
    def tearDownClass(cls):
        """在所有测试完成后执行全局清理（仅执行一次）"""
        super().tearDownClass()
        User.objects.all().delete()
        Club.objects.all().delete()
        Membership.objects.all().delete()
        NewClubRequest.objects.all().delete()
        Event.objects.all().delete()