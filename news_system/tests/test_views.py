from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from news_system.models import News, Comment
from user_system.models import User
from club_system.models import Club, Membership
from event_system.models import Event

class NewsViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 创建测试用户
        cls.user = User.objects.create_user(
            username="@testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            account_type="User",
            password="testpassword"
        )
        
        cls.another_user = User.objects.create_user(
            username="@anotheruser",
            email="another@example.com",
            first_name="Another",
            last_name="User",
            account_type="User",
            password="anotherpassword"
        )
        
        # 创建测试社团
        cls.club = Club.objects.create(
            name="Test Club",
            description="Test Club Description"
        )
        
        # 将用户设为社团管理员
        Membership.objects.create(
            user=cls.user,
            club=cls.club,
            is_manager=True
        )
        
        # 创建测试活动
        cls.event = Event.objects.create(
            name="Test Event",
            club=cls.club,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            location="Test Location",
            description="Test Event Description"
        )
        
        # 创建测试新闻
        cls.news = News.objects.create(
            title="Test News",
            content="Test News Content",
            author=cls.user,
            club=cls.club
        )
        
        # 创建测试评论
        cls.comment = Comment.objects.create(
            news=cls.news,
            text="Test Comment",
            author=cls.user
        )
        
        cls.another_comment = Comment.objects.create(
            news=cls.news,
            text="Another Comment",
            author=cls.another_user
        )
    
    def setUp(self):
        self.client = Client()
    
    def test_news_list_view(self):
        """测试新闻列表视图"""
        response = self.client.get(reverse('news_system:news_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_list.html')
        self.assertContains(response, 'Test News')
        self.assertIn('posts', response.context)
        self.assertEqual(len(response.context['posts']), 1)
    
    def test_news_list_view_with_search(self):
        """测试带搜索参数的新闻列表视图"""
        response = self.client.get(reverse('news_system:news_list') + '?q=Test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 1)
        
        response = self.client.get(reverse('news_system:news_list') + '?q=NonExistent')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 0)
    
    def test_news_list_view_with_club_filter(self):
        """测试带社团过滤的新闻列表视图"""
        response = self.client.get(reverse('news_system:news_list') + f'?club={self.club.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 1)
        
        # 创建另一个社团和新闻
        another_club = Club.objects.create(name="Another Club")
        News.objects.create(
            title="Another News",
            content="Another Content",
            author=self.user,
            club=another_club
        )
        
        response = self.client.get(reverse('news_system:news_list') + f'?club={another_club.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 1)
        self.assertContains(response, 'Another News')
    
    def test_news_list_view_with_ordering(self):
        """测试带排序的新闻列表视图"""
        # 创建另一个较新的新闻
        News.objects.create(
            title="Newer News",
            content="Newer Content",
            author=self.user,
            club=self.club
        )
        
        # 默认降序（最新的在前）
        response = self.client.get(reverse('news_system:news_list'))
        self.assertEqual(response.context['posts'][0].title, "Newer News")
        
        # 升序（最早的在前）
        response = self.client.get(reverse('news_system:news_list') + '?order=asc')
        self.assertEqual(response.context['posts'][0].title, "Test News")
    
    def test_news_detail_view(self):
        """测试新闻详情视图"""
        response = self.client.get(reverse('news_system:news_detail', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_detail.html')
        self.assertContains(response, 'Test News')
        self.assertContains(response, 'Test News Content')
        self.assertContains(response, 'Test Comment')
        self.assertIn('post', response.context)
        self.assertEqual(response.context['post'], self.news)
    
    def test_news_detail_view_with_comment_form(self):
        """测试登录用户可以看到评论表单"""
        # 未登录用户不应该看到评论表单
        response = self.client.get(reverse('news_system:news_detail', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('form', response.context)
        
        # 登录用户应该看到评论表单
        self.client.login(username='@testuser', password='testpassword')
        response = self.client.get(reverse('news_system:news_detail', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_news_detail_post_comment(self):
        """测试在新闻详情页发表评论"""
        self.client.login(username='@testuser', password='testpassword')
        form_data = {
            'text': 'New Comment from Detail View'
        }
        response = self.client.post(
            reverse('news_system:news_detail', kwargs={'pk': self.news.pk}),
            form_data
        )
        self.assertEqual(response.status_code, 302)  # 应该重定向回详情页
        self.assertTrue(Comment.objects.filter(text='New Comment from Detail View').exists())
    
    def test_news_detail_post_invalid_comment(self):
        """测试在新闻详情页提交无效评论"""
        self.client.login(username='@testuser', password='testpassword')
        form_data = {
            'text': ''  # 空评论，应该验证失败
        }
        response = self.client.post(
            reverse('news_system:news_detail', kwargs={'pk': self.news.pk}),
            form_data
        )
        self.assertEqual(response.status_code, 200)  # 应该返回表单页面
        self.assertFalse(Comment.objects.filter(text='').exists())
    
    def test_news_create_view_get(self):
        """测试新闻创建视图的GET请求"""
        # 未登录用户应该被重定向到登录页面
        response = self.client.get(reverse('news_system:news_create'))
        self.assertEqual(response.status_code, 302)
        
        # 登录用户应该能够访问创建页面
        self.client.login(username='@testuser', password='testpassword')
        response = self.client.get(reverse('news_system:news_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_form.html')
        self.assertIn('form', response.context)
    
    def test_news_create_view_post(self):
        """测试新闻创建视图的POST请求"""
        self.client.login(username='@testuser', password='testpassword')
        form_data = {
            'title': 'New Test News',
            'club': self.club.pk,
            'content': 'New Test Content'
        }
        response = self.client.post(reverse('news_system:news_create'), form_data)
        self.assertEqual(response.status_code, 302)  # 应该重定向到新闻列表页面
        
        # 验证新闻是否已创建
        self.assertTrue(News.objects.filter(title='New Test News').exists())
        new_news = News.objects.get(title='New Test News')
        self.assertEqual(new_news.author, self.user)
        self.assertEqual(new_news.club, self.club)
    
    def test_news_delete_view(self):
        """测试新闻删除视图"""
        # 创建一个新的新闻用于测试删除
        news_to_delete = News.objects.create(
            title="News To Delete",
            content="Content To Delete",
            author=self.user,
            club=self.club
        )
        
        # 未登录用户应该被重定向到登录页面
        response = self.client.get(reverse('news_system:news_delete', kwargs={'pk': news_to_delete.pk}))
        self.assertEqual(response.status_code, 302)
        
        # 登录用户（作者）应该能够访问删除页面
        self.client.login(username='@testuser', password='testpassword')
        response = self.client.get(reverse('news_system:news_delete', kwargs={'pk': news_to_delete.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_confirm_delete.html')
        
        # 执行删除
        response = self.client.post(reverse('news_system:news_delete', kwargs={'pk': news_to_delete.pk}))
        self.assertEqual(response.status_code, 302)  # 应该重定向到新闻列表页面
        
        # 验证新闻是否已删除
        self.assertFalse(News.objects.filter(pk=news_to_delete.pk).exists())
    
    def test_news_delete_view_permission(self):
        """测试非作者用户无法删除新闻"""
        # 登录另一个用户（非作者）
        self.client.login(username='@anotheruser', password='anotherpassword')
        response = self.client.get(reverse('news_system:news_delete', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 403)  # 应该返回403 Forbidden
        
        # 尝试执行删除
        response = self.client.post(reverse('news_system:news_delete', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 403)  # 应该返回403 Forbidden
        
        # 验证新闻是否仍然存在
        self.assertTrue(News.objects.filter(pk=self.news.pk).exists())
    
    def test_comment_delete_view(self):
        """测试评论删除视图"""
        # 创建一个新的评论用于测试删除
        comment_to_delete = Comment.objects.create(
            news=self.news,
            text="Comment To Delete",
            author=self.user
        )
        
        # 未登录用户应该被重定向到登录页面
        response = self.client.get(reverse('news_system:comment_delete', kwargs={'pk': comment_to_delete.pk}))
        self.assertEqual(response.status_code, 302)
        
        # 登录用户（作者）应该能够访问删除页面
        self.client.login(username='@testuser', password='testpassword')
        response = self.client.get(reverse('news_system:comment_delete', kwargs={'pk': comment_to_delete.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comment_confirm_delete.html')
        
        # 执行删除
        response = self.client.post(reverse('news_system:comment_delete', kwargs={'pk': comment_to_delete.pk}))
        self.assertEqual(response.status_code, 302)  # 应该重定向到新闻详情页面
        
        # 验证评论是否已删除
        self.assertFalse(Comment.objects.filter(pk=comment_to_delete.pk).exists())
    
    def test_comment_delete_view_permission(self):
        """测试非作者用户无法删除评论"""
        # 登录另一个用户（非作者）
        self.client.login(username='@anotheruser', password='anotherpassword')
        response = self.client.get(reverse('news_system:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 403)  # 应该返回403 Forbidden
        
        # 尝试执行删除
        response = self.client.post(reverse('news_system:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 403)  # 应该返回403 Forbidden
        
        # 验证评论是否仍然存在
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())
        
        # 但是可以删除自己的评论
        response = self.client.get(reverse('news_system:comment_delete', kwargs={'pk': self.another_comment.pk}))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('news_system:comment_delete', kwargs={'pk': self.another_comment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.another_comment.pk).exists())
    
    def test_admin_can_delete_any_comment(self):
        """测试管理员用户可以删除任何人的评论"""
        # 创建管理员用户
        admin_user = User.objects.create_user(
            username="@adminuser",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            account_type="Admin",
            password="adminpassword"
        )
        
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpassword')
        
        # 管理员应该能够访问其他用户的评论删除页面
        response = self.client.get(reverse('news_system:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 200)
        
        # 管理员应该能够删除其他用户的评论
        response = self.client.post(reverse('news_system:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
    
    def test_admin_can_delete_any_news(self):
        """测试管理员用户可以删除任何人的新闻文章"""
        # 创建管理员用户，确保用户名一致
        admin_user = User.objects.create_user(
            username="@adminuser",  # 修改为与login使用的用户名一致
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            account_type="Admin",
            password="adminpassword"
        )
        
        # 登录管理员用户
        self.client.login(username='@adminuser', password='adminpassword')
        
        # 管理员应该能够删除其他用户的新闻
        response = self.client.post(reverse('news_system:news_delete', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 302)  # 应该重定向到新闻列表页面
        # 验证新闻是否已删除
        self.assertFalse(News.objects.filter(pk=self.news.pk).exists())
    
    def test_load_events_ajax_view(self):
        """测试加载活动的AJAX视图"""
        response = self.client.get(reverse('news_system:ajax_load_events') + f'?club={self.club.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # 验证返回的JSON数据
        data = response.json()
        self.assertEqual(len(data), 1)
    
    def test_load_events_ajax_view_no_club(self):
        """测试未提供社团ID时的AJAX视图行为"""
        response = self.client.get(reverse('news_system:ajax_load_events'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)  # 应该返回空列表