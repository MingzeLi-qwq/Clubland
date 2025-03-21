from django.test import TestCase, Client
from django.urls import reverse
from user_system.models import User
from club_system.models import Club, Membership, NewClubRequest
from event_system.models import Event, RSVP
from django.utils import timezone
from datetime import timedelta

class AdminSystemViewsTest(TestCase):
    def setUp(self):
        # 创建测试客户端
        self.client = Client()
        
        # 创建管理员用户
        self.admin_user = User.objects.create_user(
            username="@adminuser",
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            account_type="Admin"
        )
        
        # 创建普通用户
        self.normal_user = User.objects.create_user(
            username="@normaluser",
            email="normal@example.com",
            password="normalpass123",
            first_name="Normal",
            last_name="User",
            account_type="User"
        )
        
        # 创建俱乐部管理员用户
        self.club_manager = User.objects.create_user(
            username="@clubmanager",
            email="manager@example.com",
            password="managerpass123",
            first_name="Club",
            last_name="Manager",
            account_type="User"
        )
        
        # 创建测试俱乐部
        self.club = Club.objects.create(
            name="Test Club",
            description="Test Description"
        )
        
        # 创建另一个测试俱乐部
        self.another_club = Club.objects.create(
            name="Another Club",
            description="Another Description"
        )
        
        # 创建成员关系
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
        
        # 创建测试事件
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Event Description",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=2),
            location="Test Location",
            club=self.club
        )

    def test_admin_panel_clubs_view(self):
        """测试管理员面板俱乐部列表视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问俱乐部列表页面
        response = self.client.get(reverse('admin_panel_clubs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/clubs.html')
        
        # 测试搜索功能 - 搜索存在的俱乐部
        response = self.client.get(reverse('admin_panel_clubs'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clubs']), 1)
        self.assertEqual(response.context['clubs'][0].name, 'Test Club')
        
        # 测试搜索功能 - 搜索不存在的俱乐部
        response = self.client.get(reverse('admin_panel_clubs'), {'search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clubs']), 0)

    def test_admin_panel_users_view(self):
        """测试管理员面板用户列表视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问用户列表页面
        response = self.client.get(reverse('admin_panel_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/users.html')
        
        # 测试搜索功能 - 搜索存在的用户
        response = self.client.get(reverse('admin_panel_users'), {'search': 'Normal'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 1)
        self.assertEqual(response.context['users'][0].username, '@normaluser')
        
        # 测试搜索功能 - 搜索不存在的用户
        response = self.client.get(reverse('admin_panel_users'), {'search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 0)

    def test_admin_panel_requests_view(self):
        """测试管理员面板请求列表视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问请求列表页面
        response = self.client.get(reverse('admin_panel_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/requests.html')

    def test_admin_panel_clubs_general_view(self):
        """测试管理员面板俱乐部一般信息视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问俱乐部一般信息页面
        response = self.client.get(reverse('admin_panel_club_general', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/general.html')
        
        # 检查上下文数据
        self.assertIn('club', response.context)
        self.assertIn('club_id', response.context)
        self.assertEqual(response.context['club'].name, 'Test Club')
        self.assertEqual(response.context['club_id'], self.club.pk)

    def test_admin_panel_clubs_members_view(self):
        """测试管理员面板俱乐部成员列表视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问俱乐部成员列表页面
        response = self.client.get(reverse('admin_panel_club_members', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/members.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['manager_count'], 1)
        self.assertEqual(response.context['muggle_count'], 1)
        
        # 测试管理员搜索功能
        response = self.client.get(reverse('admin_panel_club_members', args=[self.club.pk]), {'manager_search': 'Club'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['managers']), 1)
        self.assertEqual(response.context['managers'][0].user.username, '@clubmanager')
        
        # 测试普通成员搜索功能
        response = self.client.get(reverse('admin_panel_club_members', args=[self.club.pk]), {'member_search': 'Normal'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['muggles']), 1)
        self.assertEqual(response.context['muggles'][0].user.username, '@normaluser')
        
        # 测试搜索不存在的成员
        response = self.client.get(reverse('admin_panel_club_members', args=[self.club.pk]), {'member_search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['muggles']), 0)

    def test_admin_panel_clubs_news_view(self):
        """测试管理员面板俱乐部新闻视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问俱乐部新闻页面
        response = self.client.get(reverse('admin_panel_club_news', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/news.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['club_id'], self.club.pk)

    def test_admin_panel_clubs_dashboard_view(self):
        """测试管理员面板俱乐部仪表盘视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问俱乐部仪表盘页面
        response = self.client.get(reverse('admin_panel_club_dashboard', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/dashboard.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['club_id'], self.club.pk)

    def test_admin_panel_clubs_events_view(self):
        """测试管理员面板俱乐部事件列表视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 创建另一个测试事件用于测试搜索功能
        another_event = Event.objects.create(
            name="Another Event",
            description="Another Event Description",
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=2),
            location="Another Location",
            club=self.club
        )
        
        # 访问俱乐部事件列表页面
        response = self.client.get(reverse('admin_panel_club_events', args=[self.club.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/events.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(len(response.context['events']), 2)  # 应该有两个事件
        
        # 测试搜索功能 - 搜索存在的事件
        response = self.client.get(reverse('admin_panel_club_events', args=[self.club.pk]), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events']), 1)
        self.assertEqual(response.context['events'][0].name, 'Test Event')
        
        # 测试搜索功能 - 搜索不存在的事件
        response = self.client.get(reverse('admin_panel_club_events', args=[self.club.pk]), {'search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events']), 0)
        
        # 清理测试数据
        another_event.delete()

    def test_admin_delete_club_view(self):
        """测试管理员删除俱乐部功能"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 创建一个新的俱乐部用于测试删除功能
        test_delete_club = Club.objects.create(
            name="Test Delete Club",
            description="This club will be deleted"
        )
        
        # 测试未验证密码时的POST请求
        response = self.client.post(reverse('admin_delete_club', args=[test_delete_club.pk]))
        
        # 应该重定向到密码验证页面
        self.assertRedirects(response, reverse('verify_admin_password'))
        
        # 检查session中是否设置了正确的值
        self.assertEqual(self.client.session['pending_action'], 'delete_club')
        self.assertEqual(self.client.session['club_id'], test_delete_club.pk)
        self.assertEqual(
            self.client.session['return_url'], 
            reverse('admin_panel_club_general', kwargs={'club_id': test_delete_club.pk})
        )
        
        # 模拟密码验证成功 - 使用新的会话
        session = self.client.session
        session['password_verified'] = True
        session.save()
        
        # 测试已验证密码时的GET请求
        response = self.client.get(reverse('admin_delete_club', args=[test_delete_club.pk]))
        self.assertRedirects(response, reverse('admin_panel_clubs'))
        self.assertEqual(Club.objects.filter(pk=test_delete_club.pk).count(), 0)
        self.assertNotIn('password_verified', self.client.session)

    def test_admin_panel_clubs_event_general_view(self):
        """测试管理员面板俱乐部事件详情视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问俱乐部事件详情页面
        response = self.client.get(reverse('admin_panel_club_event_general', args=[self.club.pk, self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/admin_panel_club_event/general.html')

        # 检查上下文数据
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['event'], self.event)
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(response.context['event_id'], self.event.pk)

    def test_admin_panel_clubs_event_rsvps_view(self):
        """测试管理员面板俱乐部事件RSVP列表视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 创建测试RSVP
        test_rsvp = RSVP.objects.create(
            user=self.normal_user,
            event=self.event
        )
        
        # 创建另一个用户和RSVP用于测试搜索功能
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
        
        # 访问事件RSVP列表页面
        response = self.client.get(reverse('admin_panel_club_event_RSVPs', args=[self.club.pk, self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_club/admin_panel_club_event/RSVPs.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['club'], self.club)
        self.assertEqual(response.context['event'], self.event)
        self.assertEqual(response.context['club_id'], self.club.pk)
        self.assertEqual(len(response.context['rsvps']), 2)  # 应该有两个RSVP
        
        # 测试搜索功能 - 搜索存在的用户
        response = self.client.get(
            reverse('admin_panel_club_event_RSVPs', args=[self.club.pk, self.event.pk]), 
            {'search': 'Search'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rsvps']), 1)
        self.assertEqual(response.context['rsvps'][0].user.first_name, 'Search')
        
        # 测试搜索功能 - 搜索不存在的用户
        response = self.client.get(
            reverse('admin_panel_club_event_RSVPs', args=[self.club.pk, self.event.pk]), 
            {'search': 'NonExistent'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rsvps']), 0)
        
        # 清理测试数据
        test_rsvp.delete()
        another_rsvp.delete()
        another_user.delete()

    def test_admin_panel_user_information_view(self):
        """测试管理员面板用户信息视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 访问用户信息页面
        response = self.client.get(reverse('admin_panel_user_information', args=[self.normal_user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_user/information.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['panel_user'], self.normal_user)
        self.assertEqual(response.context['panel_username'], self.normal_user.username)

    def test_admin_panel_user_memberships_view(self):
        """测试管理员面板用户会员资格视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 创建另一个俱乐部和会员资格用于测试
        another_club = Club.objects.create(
            name="Another Test Club",
            description="Another Test Club Description"
        )
        
        # 为普通用户创建一个新的会员资格（在另一个俱乐部中）
        # 注意：self.normal_user 在 setUp 中已经与 self.club 建立了会员关系
        regular_membership = Membership.objects.create(
            user=self.normal_user,
            club=another_club,
            is_manager=False
        )
        
        # 访问用户会员资格页面
        response = self.client.get(reverse('admin_panel_user_memberships', args=[self.normal_user.username]))
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_user/memberships.html')

        self.assertEqual(response.context['panel_user'], self.normal_user)
        self.assertEqual(response.context['panel_username'], self.normal_user.username)
        
        # 检查会员资格数量
        # 假设 setUp 中的会员资格是管理员，另一个是普通成员
        managers = response.context['managers']
        regulars = response.context['regulars']
        
        # 检查会员资格数量和类型
        self.assertEqual(response.context['manager_count'], 0)  # 假设 setUp 中没有设置为管理员
        self.assertEqual(response.context['regular_count'], 2)  # 应该有两个普通成员资格
        
        # 测试搜索功能
        response = self.client.get(
            reverse('admin_panel_user_memberships', args=[self.normal_user.username]),
            {'search': 'Another Test'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['manager_count'], 0)
        self.assertEqual(response.context['regular_count'], 1)
        self.assertEqual(response.context['regulars'][0].club.name, 'Another Test Club')
        
        # 清理测试数据
        regular_membership.delete()
        another_club.delete()

    def test_admin_panel_remove_memberships_view(self):
        """测试管理员删除用户会员资格功能"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 确认会员资格已创建
        self.assertEqual(
            Membership.objects.filter(user=self.normal_user, club=self.club).count(),1
        )
        
        # 发送删除请求
        response = self.client.post(
            reverse('admin_panel_remove_memberships', args=[self.normal_user.username, self.club.pk])
        )
        
        # 检查是否重定向到用户会员资格页面
        self.assertRedirects(
            response, 
            reverse('admin_panel_user_memberships', args=[self.normal_user.username])
        )
        
        # 检查会员资格是否已被删除
        self.assertEqual(
            Membership.objects.filter(user=self.normal_user, club=self.club).count(),0
        )
        
        # # 检查是否有成功消息
        # messages = list(get_messages(response.wsgi_request))
        # self.assertTrue(any(f"Removed membership from {self.club.name}" in str(message) for message in messages))

    def test_admin_panel_new_club_requests_view(self):
        """测试管理员面板新俱乐部请求列表视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 创建测试新俱乐部请求
        pending_request = NewClubRequest.objects.create(
            name="Pending Test Club",
            description="Pending Test Club Description",
            creator=self.normal_user,
            status='pending'
        )
        
        # 访问新俱乐部请求列表页面
        response = self.client.get(reverse('admin_panel_new_club_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_requests/new_club_requests.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['pending_count'], 1)
        self.assertEqual(list(response.context['pending_ncRequests']), [pending_request])
        
        # 测试搜索功能 - 搜索存在的请求
        response = self.client.get(reverse('admin_panel_new_club_requests'), {'search': 'Pending'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pending_count'], 1)
        self.assertEqual(list(response.context['pending_ncRequests']), [pending_request])
        
        # 清理测试数据
        pending_request.delete()

    def test_admin_panel_new_club_request_detail_view(self):
        """测试管理员面板新俱乐部请求详情视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 创建测试新俱乐部请求
        test_request = NewClubRequest.objects.create(
            name="Test Detail Club",
            description="Test Detail Club Description",
            creator=self.normal_user,
            status='pending'
        )
        
        # 访问新俱乐部请求详情页面
        response = self.client.get(reverse('admin_panel_new_club_requests_detail', args=[test_request.request_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_requests/new_club_request_detail.html')
        
        # 检查上下文数据
        self.assertEqual(response.context['ncRequest'], test_request)
        self.assertEqual(response.context['creator'], self.normal_user)
        
        # 清理测试数据
        test_request.delete()

    def test_admin_review_new_club_request_view(self):
        """测试管理员审核新俱乐部请求视图"""
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpass123')
        
        # 创建测试新俱乐部请求
        test_request = NewClubRequest.objects.create(
            name="Test Review Club",
            description="Test Review Club Description",
            creator=self.normal_user,
            status='pending'
        )
        
        # 测试 GET 请求
        response = self.client.get(reverse('admin_review_new_club_request', args=[test_request.request_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel/admin_panel_requests/new_club_request_detail.html')

        self.assertEqual(response.context['ncRequest'], test_request)
        
        # 测试 POST 请求 - 接受俱乐部请求
        response = self.client.post(
            reverse('admin_review_new_club_request', args=[test_request.request_id]),
            {
                'action': 'accept',
                'review': 'This is a good club idea.'
            }
        )
        
        # 检查是否重定向到新俱乐部请求列表页面
        self.assertRedirects(response, reverse('admin_panel_new_club_requests'))
        
        # 重新获取更新后的请求对象
        test_request.refresh_from_db()
        
        # 检查请求状态是否已更新为已批准
        self.assertEqual(test_request.status, NewClubRequest.STATUS_APPROVED)
        self.assertEqual(test_request.review, 'This is a good club idea.')
        self.assertEqual(test_request.reviewed_by, self.admin_user)
        
        # 检查是否创建了新俱乐部
        self.assertTrue(Club.objects.filter(name="Test Review Club").exists())
        new_club = Club.objects.get(name="Test Review Club")
        
        # 检查是否创建了会员资格
        self.assertTrue(Membership.objects.filter(user=self.normal_user, club=new_club, is_manager=True).exists())
        
        # 创建另一个测试请求用于测试拒绝功能
        reject_request = NewClubRequest.objects.create(
            name="Test Reject Club",
            description="Test Reject Club Description",
            creator=self.normal_user,
            status='pending'
        )
        
        # 测试 POST 请求 - 拒绝俱乐部请求
        response = self.client.post(
            reverse('admin_review_new_club_request', args=[reject_request.request_id]),
            {
                'action': 'reject',
                'review': 'This club idea is not suitable.'
            }
        )
        
        # 检查是否重定向到新俱乐部请求列表页面
        self.assertRedirects(response, reverse('admin_panel_new_club_requests'))
        
        # 重新获取更新后的请求对象
        reject_request.refresh_from_db()
        
        # 检查请求状态是否已更新为已拒绝
        self.assertEqual(reject_request.status, NewClubRequest.STATUS_REJECTED)
        self.assertEqual(reject_request.review, 'This club idea is not suitable.')
        self.assertEqual(reject_request.reviewed_by, self.admin_user)
        
        # 清理测试数据
        new_club.delete()
        test_request.delete()
        reject_request.delete()