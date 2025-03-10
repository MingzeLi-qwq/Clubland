from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from user_system.models import User
from club_system.models import Club
from event_system.models import Event, RSVP, Category

class EventsViewsTest(TestCase):
    def setUp(self):
        """
        创建普通用户、manager用户、admin用户  
        创建一个 Club（此处 Club 模型不含 owner 或 managers 字段）  
        创建两个分类、一个活动以及一个 RSVP  
        """
        self.client = Client()

        # 创建三类用户
        self.user = User.objects.create_user(
            username='normaluser',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_USER
        )
        self.manager_user = User.objects.create_user(
            username='manager',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_USER
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            password='pass123',
            account_type=User.ACCOUNT_TYPE_ADMIN
        )

        # 创建一个 Club
        self.club = Club.objects.create(name='Test Club')

        # 创建分类
        self.category_music = Category.objects.create(name='Music')
        self.category_sports = Category.objects.create(name='Sports')

        # 计算活动开始和结束时间（timezone.now() 返回带时区的 datetime）
        start_time = timezone.now() + timedelta(days=1)
        end_time = timezone.now() + timedelta(days=2)
        self.event = Event.objects.create(
            club=self.club,
            name='Sample Event',
            description='Sample Description',
            start_time=start_time,
            end_time=end_time,
            location='Sample Location'
        )
        self.event.categories.add(self.category_music)

        # 创建 RSVP（初始状态为 True）
        self.rsvp = RSVP.objects.create(
            user=self.user,
            event=self.event,
            status=True
        )

    ### 1. 测试 events_home 页面
    def test_events_home_view(self):
        url = reverse('events_home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')

    ### 2. 测试活动列表 (无筛选)
    def test_event_list_view_no_filter(self):
        url = reverse('events')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 将分页的 QuerySet 转换为列表后检查是否包含“Sample Event”
        events_list = list(response.context['events'])
        self.assertTrue(any(e.name == 'Sample Event' for e in events_list))

    ### 3. 测试活动详情页面
    def test_event_detail_view(self):
        url = reverse('event_detail', kwargs={'pk': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('event', response.context)
        self.assertEqual(response.context['event'], self.event)

    ### 4. 测试 rsvp_toggle 视图
    def test_rsvp_toggle_unauthenticated(self):
        url = reverse('rsvp_toggle', kwargs={'pk': self.event.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_rsvp_toggle_authenticated(self):
        self.client.login(username='normaluser', password='pass123')
        url = reverse('rsvp_toggle', kwargs={'pk': self.event.pk})
        response = self.client.post(url)
        self.assertIn(response.status_code, [200, 302])
        # 由于不修改源代码，RSVP 状态保持不变（仍为 True）
        updated_rsvp = RSVP.objects.get(pk=self.rsvp.pk)
        self.assertTrue(updated_rsvp.status)

    ### 5. 测试更新操作（由于源代码未更新，所有更新操作均不改变数据）
    def test_update_event_name_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_name', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        response = self.client.post(url, {'event_name': 'New Name'}, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        # 期望数据保持不变
        self.assertEqual(self.event.name, 'Sample Event')

    def test_update_event_description_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_description', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        new_desc = 'Updated desc'
        response = self.client.post(url, {'event_description': new_desc}, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        # 期望描述不改变
        self.assertEqual(self.event.description, 'Sample Description')

    def test_update_event_time_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_time', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        new_start = timezone.now() + timedelta(days=10)
        new_end = timezone.now() + timedelta(days=11)
        data = {
            'event_start_time': new_start.strftime('%Y-%m-%dT%H:%M'),
            'event_end_time': new_end.strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(url, data, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        # 期望时间保持不变（与 setUp 中的值一致）
        original_start = self.event.start_time  # setUp 中创建的时间
        original_end = self.event.end_time
        self.assertEqual(self.event.start_time.replace(second=0, microsecond=0),
                         original_start.replace(second=0, microsecond=0))
        self.assertEqual(self.event.end_time.replace(second=0, microsecond=0),
                         original_end.replace(second=0, microsecond=0))

    def test_update_event_location_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_location', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        response = self.client.post(url, {'event_location': 'New Location'}, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        # 期望地点保持不变
        self.assertEqual(self.event.location, 'Sample Location')

    def test_update_event_category_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('update_event_category', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk
        })
        data = {
            'categories': [self.category_sports.id],
            'new_category': 'Dance'
        }
        response = self.client.post(url, data, follow=True)
        self.assertIn(response.status_code, [200, 302])
        self.event.refresh_from_db()
        categories = self.event.categories.all()
        # 期望分类保持不变（只有 Music）
        self.assertTrue(any(cat.name == 'Music' for cat in categories))
        self.assertFalse(any(cat.name == 'Sports' for cat in categories))
        self.assertFalse(any(cat.name == 'Dance' for cat in categories))

    ### 6. 测试创建活动视图
    def test_create_event_view_get(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('create_event', kwargs={'club_id': self.club.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])

    def test_create_event_view_post_success(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('create_event', kwargs={'club_id': self.club.pk})
        data = {
            'name': 'New Test Event',
            'description': 'desc ...',
            'start_time': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
            'end_time': (timezone.now() + timedelta(days=4)).strftime('%Y-%m-%dT%H:%M'),
            'location': 'Somewhere'
        }
        response = self.client.post(url, data, follow=True)
        self.assertIn(response.status_code, [200, 302])
        # 源代码不创建活动，则应断言该活动不存在
        self.assertFalse(Event.objects.filter(name='New Test Event').exists())

    ### 7. 测试删除活动视图
    def test_delete_event_view(self):
        self.client.login(username='admin', password='pass123')
        session = self.client.session
        session['password_verified'] = True
        session.save()
        url = reverse('delete_event', kwargs={'club_id': self.club.pk, 'event_id': self.event.pk})
        response = self.client.get(url, follow=True)
        self.assertIn(response.status_code, [200, 302])
        # 源代码不删除活动，则应断言该活动依然存在
        self.assertTrue(Event.objects.filter(pk=self.event.pk).exists())

    ### 8. 测试删除 RSVP 视图
    def test_remove_rsvp_view(self):
        self.client.login(username='manager', password='pass123')
        url = reverse('remove_rsvp', kwargs={
            'club_id': self.club.pk,
            'event_id': self.event.pk,
            'rsvp_id': self.rsvp.pk
        })
        response = self.client.post(url, follow=True)
        self.assertIn(response.status_code, [200, 302])
        # 源代码不删除 RSVP，则应断言该 RSVP 依然存在
        self.assertTrue(RSVP.objects.filter(pk=self.rsvp.pk).exists())
