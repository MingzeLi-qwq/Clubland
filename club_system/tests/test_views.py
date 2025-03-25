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
        
        # Creating a Normal Test User
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

        # Create administrator user (no membership with club)
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
        

    def test_isSameClubNameExistInRequest(self):
        """Test if the isSameClubNameExistInRequest function correctly detects duplicate club request names"""
        # Test the exact same name
        self.assertTrue(isSameClubNameExistInRequest("New Test Club"))
        
        # Testing different names
        self.assertFalse(isSameClubNameExistInRequest("Different Club Request"))
        
        # Tests Ignore Case
        self.assertTrue(isSameClubNameExistInRequest("NEW TEST CLUB"))
        self.assertTrue(isSameClubNameExistInRequest("new test club"))
        
        # Test Ignore Spaces
        self.assertTrue(isSameClubNameExistInRequest("NewTestClub"))
        self.assertTrue(isSameClubNameExistInRequest("New  Test  Club"))
        self.assertTrue(isSameClubNameExistInRequest(" New Test Club "))
        
        # Test for ignoring both case and spaces
        self.assertTrue(isSameClubNameExistInRequest("NEWTESTCLUB"))
        self.assertTrue(isSameClubNameExistInRequest("new  test  club"))


    def test_club_manager_members_view(self):
        """Test Club manager Member Page View"""
        self.client.login(username='@manageruser', password='managerpass123')
        
        response = self.client.get(reverse('club_manager_members', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_manager/members.html')
        
        # Examining Contextual Data
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
        
        # The new description cannot duplicate the old description
        self.client.login(username='@manageruser', password='managerpass123')
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
        
        # Check if another manager has been removed
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
        
        # Logging in as an manager user
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
        
        # Test removing users who do not belong to the club
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