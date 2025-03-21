from django.test import TestCase, Client, RequestFactory
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import AnonymousUser
from news_system.models import News, Comment
from news_system.forms import NewsForm, CommentForm
from news_system.views import (
    get_first_image_url,
    enhance_news_with_image,
    NewsListView,
    NewsDetailView,
    NewsCreateView,
    CommentCreateView,
    NewsDeleteView,
    CommentDeleteView,
    load_events
)
from user_system.models import User
from club_system.models import Club, Membership
from event_system.models import Event
from CMS_mixins.CMS_utils import RTEUploadUtils

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
        cls.admin_user = User.objects.create_user(
            username="@adminuser",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            account_type="Admin",
            password="adminpassword"
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
        # 创建另一篇较新的新闻
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
        posts_list = list(response.context['posts'])
        self.assertEqual(posts_list[0].title, "Test News")
    
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
        # 未登录用户不应显示评论表单
        response = self.client.get(reverse('news_system:news_detail', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('form', response.context)
        # 登录用户应显示评论表单
        self.client.login(username='@testuser', password='testpassword')
        response = self.client.get(reverse('news_system:news_detail', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_news_detail_post_comment(self):
        """测试在新闻详情页发表评论"""
        self.client.login(username='@testuser', password='testpassword')
        form_data = {'text': 'New Comment from Detail View'}
        response = self.client.post(
            reverse('news_system:news_detail', kwargs={'pk': self.news.pk}),
            form_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='New Comment from Detail View').exists())
    
    def test_news_detail_post_invalid_comment(self):
        """测试在新闻详情页提交无效评论"""
        self.client.login(username='@testuser', password='testpassword')
        form_data = {'text': ''}
        response = self.client.post(
            reverse('news_system:news_detail', kwargs={'pk': self.news.pk}),
            form_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(text='').exists())
    
    def test_news_create_view_get(self):
        """测试新闻创建视图的GET请求"""
        # 未登录用户应重定向到登录页
        response = self.client.get(reverse('news_system:news_create'))
        self.assertEqual(response.status_code, 302)
        # 登录用户可访问创建页面
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
        self.assertEqual(response.status_code, 302)
        self.assertTrue(News.objects.filter(title='New Test News').exists())
        new_news = News.objects.get(title='New Test News')
        self.assertEqual(new_news.author, self.user)
        self.assertEqual(new_news.club, self.club)
    
    def test_news_delete_view(self):
        """测试新闻删除视图"""
        news_to_delete = News.objects.create(
            title="News To Delete",
            content="Content To Delete",
            author=self.user,
            club=self.club
        )
        self.client.login(username='@testuser', password='testpassword')
        # GET 请求调用 get_success_url 时未设置 self.object，预期抛出异常
        with self.assertRaises(AttributeError):
            self.client.get(reverse('news_system:news_delete', kwargs={'pk': news_to_delete.pk}))
        # AJAX POST 请求删除新闻
        response = self.client.post(
            reverse('news_system:news_delete', kwargs={'pk': news_to_delete.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        self.assertFalse(News.objects.filter(pk=news_to_delete.pk).exists())
    
    def test_news_delete_permission(self):
        """测试非作者登录用户删除新闻时返回403"""
        self.client.login(username='@anotheruser', password='anotherpassword')
        response = self.client.post(reverse('news_system:news_delete', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 403)
    
    def test_news_delete_ajax(self):
        """测试 AJAX 请求删除新闻"""
        self.client.login(username='@testuser', password='testpassword')
        response = self.client.post(
            reverse('news_system:news_delete', kwargs={'pk': self.news.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
    
    def test_news_delete_non_ajax(self):
        """测试非 AJAX 删除新闻"""
        self.client.login(username='@testuser', password='testpassword')
        response = self.client.post(reverse('news_system:news_delete', kwargs={'pk': self.news.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(News.objects.filter(pk=self.news.pk).exists())
    
    def test_news_create_invalid_form(self):
        """测试提交无效新闻表单"""
        self.client.login(username='@testuser', password='testpassword')
        form_data = {'title': '', 'content': 'Valid Content'}
        response = self.client.post(reverse('news_system:news_create'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
    
    def test_comment_delete_view(self):
        """测试评论删除视图"""
        comment_to_delete = Comment.objects.create(
            news=self.news,
            text="Comment To Delete",
            author=self.user
        )
        response = self.client.get(reverse('news_system:comment_delete', kwargs={'pk': comment_to_delete.pk}))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='@testuser', password='testpassword')
        response = self.client.get(reverse('news_system:comment_delete', kwargs={'pk': comment_to_delete.pk}))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            reverse('news_system:comment_delete', kwargs={'pk': comment_to_delete.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        self.assertFalse(Comment.objects.filter(pk=comment_to_delete.pk).exists())
    
    def test_comment_delete_view_permission(self):
        """测试非作者不能删除评论"""
        self.client.login(username='@anotheruser', password='anotherpassword')
        response = self.client.post(reverse('news_system:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(response.status_code, 403)
    
    def test_admin_can_delete_any_comment(self):
        """测试管理员用户可以删除任何人的评论"""
        self.client.login(username='@adminuser', password='adminpassword')
        response = self.client.post(
            reverse('news_system:comment_delete', kwargs={'pk': self.comment.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
    
    def test_admin_can_delete_any_news(self):
        """测试管理员用户可以删除任何人的新闻文章"""
        self.client.login(username='@adminuser', password='adminpassword')
        response = self.client.post(
            reverse('news_system:news_delete', kwargs={'pk': self.news.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        self.assertFalse(News.objects.filter(pk=self.news.pk).exists())
    
    def test_load_events_ajax_view(self):
        """测试加载活动的AJAX视图"""
        response = self.client.get(reverse('news_system:ajax_load_events') + f'?club={self.club.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(len(data), 1)
    
    def test_load_events_ajax_view_no_club(self):
        """测试未提供社团ID时的AJAX视图行为"""
        response = self.client.get(reverse('news_system:ajax_load_events'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)

# ------------------------------
# 额外视图测试（辅助函数、部分 get_context_data 分支等）
# ------------------------------
class ExtraViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 创建测试数据
        cls.user = User.objects.create_user(
            username="@extratest",
            email="extra@example.com",
            password="testpassword"
        )
        cls.club = Club.objects.create(
            name="Extra Club",
            description="Extra Club Description"
        )
        cls.event = Event.objects.create(
            name="Extra Event",
            club=cls.club,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            location="Extra Location",
            description="Extra Event Description"
        )
        # 创建一篇新闻，内容包含图片
        cls.news = News.objects.create(
            title="Extra News",
            content='<p>Extra content <img src="http://example.com/img.jpg" /></p>',
            author=cls.user,
            club=cls.club
        )
    
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
    
    def test_get_first_image_url_with_image(self):
        """测试 get_first_image_url 当内容包含图片时返回正确的URL"""
        html = '<div><img src="http://example.com/test.jpg" alt="test"></div>'
        url = get_first_image_url(html)
        self.assertEqual(url, "http://example.com/test.jpg")
    
    def test_get_first_image_url_without_image(self):
        """测试 get_first_image_url 当内容不包含图片时返回 None"""
        html = "<div>No image here</div>"
        url = get_first_image_url(html)
        self.assertIsNone(url)
    
    def test_enhance_news_with_image(self):
        """测试 enhance_news_with_image 返回的数据包含 first_image_url"""
        data = enhance_news_with_image(self.news)
        self.assertEqual(data['id'], self.news.id)
        self.assertEqual(data['title'], self.news.title)
        self.assertEqual(data['first_image_url'], "http://example.com/img.jpg")
        self.assertEqual(data['url'], f"/news/{self.news.id}/")
    
    def test_news_list_view_queryset_search(self):
        """通过传入搜索参数 q 覆盖 NewsListView.get_queryset() 中的分支"""
        request = self.factory.get('/news/?q=Extra')
        request.user = self.user
        view = NewsListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        posts = response.context_data.get('posts')
        self.assertTrue(any("Extra" in post.title for post in posts))
    
    def test_news_list_view_queryset_ordering(self):
        """测试 NewsListView.get_queryset() 中排序分支"""
        request = self.factory.get('/news/?order=asc')
        request.user = self.user
        view = NewsListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        posts_list = list(response.context_data.get('posts'))
        self.assertEqual(posts_list[0].title, "Extra News")
    
    def test_news_detail_view_context_form(self):
        """测试 NewsDetailView.get_context_data 添加评论表单的分支"""
        request = self.factory.get('/news/1/')
        request.user = self.user
        view = NewsDetailView.as_view()
        response = view(request, pk=self.news.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context_data)
    
    def test_news_detail_view_context_remove_existing_form(self):
        """测试 NewsDetailView.get_context_data 当 context 中已有 'form' 键时正确删除并替换"""
        view = NewsDetailView()
        request = self.factory.get('/news/1/')
        request.user = self.user
        view.request = request
        view.object = self.news
        view.get_form = lambda: "new_form"
        context = view.get_context_data(form="old_form")
        self.assertNotEqual(context.get('form'), "old_form")
        self.assertEqual(context.get('form'), "new_form")
    
    def test_news_detail_view_post_invalid(self):
        """测试 NewsDetailView.post 调用 form_invalid 分支（提交无效数据）"""
        request = self.factory.post('/news/1/', data={'text': ''})
        request.user = self.user
        view = NewsDetailView.as_view()
        response = view(request, pk=self.news.pk)
        self.assertEqual(response.status_code, 200)
        # 增加断言，确保表单验证失败
        self.assertTrue(response.context_data['form'].errors)
    
    def test_news_detail_post_not_authenticated(self):
        """测试 NewsDetailView.post 当用户未登录时重定向到登录页"""
        request = self.factory.post('/news/1/', data={'text': 'Some comment'})
        request.user = AnonymousUser()
        view = NewsDetailView.as_view()
        response = view(request, pk=self.news.pk)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
    
    def test_news_detail_view_get_success_url(self):
        """测试 NewsDetailView.get_success_url 返回当前请求路径"""
        view = NewsDetailView()
        request = self.factory.get('/test_path/')
        request.user = self.user
        view.request = request
        url = view.get_success_url()
        self.assertEqual(url, '/test_path/')
    
    def test_news_create_view_form_invalid(self):
        """测试 NewsCreateView 的 form_invalid 分支，通过提交无效数据触发错误信息输出"""
        self.client.login(username='@extratest', password='testpassword')
        response = self.client.post(reverse('news_system:news_create'), {'content': 'Missing title and club'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
    
    def test_comment_create_view_get_success_url(self):
        """测试 CommentCreateView 的 get_success_url 方法"""
        view = CommentCreateView()
        view.kwargs = {'news_id': self.news.id}
        url = view.get_success_url()
        self.assertEqual(url, reverse('news_system:news_detail', kwargs={'pk': self.news.id}))
    
    def test_comment_create_view_post(self):
        """测试 CommentCreateView 的 POST 提交分支"""
        factory = RequestFactory()
        request = factory.post('/fake-url/', data={'text': 'Test comment create'})
        request.user = self.user
        view = CommentCreateView.as_view()
        response = view(request, news_id=self.news.pk)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='Test comment create', news=self.news).exists())
    
    def test_comment_delete_view_non_ajax(self):
        """测试 CommentDeleteView 非 AJAX POST 分支"""
        comment = Comment.objects.create(
            news=self.news,
            text="Extra Comment",
            author=self.user
        )
        self.client.login(username='@extratest', password='testpassword')
        response = self.client.post(reverse('news_system:comment_delete', kwargs={'pk': comment.pk}))
        self.assertEqual(response.status_code, 302)
    
    def test_comment_delete_view_get(self):
        """测试 CommentDeleteView 的 GET 请求分支"""
        comment = Comment.objects.create(
            news=self.news,
            text="Extra Comment GET",
            author=self.user
        )
        self.client.login(username='@extratest', password='testpassword')
        response = self.client.get(reverse('news_system:comment_delete', kwargs={'pk': comment.pk}))
        self.assertEqual(response.status_code, 302)
    
    def test_news_delete_view_post_non_ajax(self):
        """测试 NewsDeleteView 的非 AJAX POST 分支"""
        news_to_delete = News.objects.create(
            title="Non AJAX Delete",
            content="Content",
            author=self.user,
            club=self.club
        )
        self.client.login(username='@extratest', password='testpassword')
        response = self.client.post(reverse('news_system:news_delete', kwargs={'pk': news_to_delete.pk})) 
        self.assertEqual(response.status_code, 302)
        self.assertFalse(News.objects.filter(pk=news_to_delete.pk).exists())

# ------------------------------
# 直接调用 DeleteView.delete() 方法的测试，确保非 AJAX 分支被执行
# ------------------------------
class DeleteMethodDirectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="@directuser",
            email="direct@example.com",
            password="testpassword"
        )
        cls.club = Club.objects.create(
            name="Direct Club",
            description="Direct Club Description"
        )
        cls.news = News.objects.create(
            title="Direct Delete News",
            content="Some Content",
            author=cls.user,
            club=cls.club
        )
        cls.comment = Comment.objects.create(
            news=cls.news,
            text="Direct Delete Comment",
            author=cls.user
        )
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_news_delete_method_non_ajax(self):
        """直接调用 NewsDeleteView.delete() 的非 AJAX 分支"""
        request = self.factory.post('/dummy-url/')
        request.user = self.user
        view = NewsDeleteView()
        view.request = request
        view.kwargs = {'pk': self.news.pk}
        view.object = self.news
        response = view.delete(request, pk=self.news.pk)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(News.objects.filter(pk=self.news.pk).exists())
    
    def test_comment_delete_method_non_ajax(self):
        """直接调用 CommentDeleteView.delete() 的非 AJAX 分支"""
        request = self.factory.post('/dummy-url/')
        request.user = self.user
        view = CommentDeleteView()
        view.request = request
        view.kwargs = {'pk': self.comment.pk}
        view.object = self.comment
        response = view.delete(request, pk=self.comment.pk)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())