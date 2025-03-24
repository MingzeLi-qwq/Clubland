from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from user_system.models import User
from club_system.models import Club, Membership
from .models import BlogPost, ThreadPost
from .forms import BlogPostForm, ThreadPostForm

class BlogPostModelTest(TestCase):
    """测试BlogPost模型"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # 创建测试社团
        self.club = Club.objects.create(
            name='Test Club',
            description='This is a test club'
        )
        
        # 创建测试博客
        self.blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            content='This is a test blog post content.',
            author=self.user,
            club=self.club
        )
    
    def test_blog_post_creation(self):
        """测试博客文章是否被正确创建"""
        self.assertEqual(self.blog_post.title, 'Test Blog Post')
        self.assertEqual(self.blog_post.author, self.user)
        self.assertEqual(self.blog_post.club, self.club)
        self.assertTrue(self.blog_post.created_at <= timezone.now())
    
    def test_blog_post_str_representation(self):
        """测试博客文章的字符串表示"""
        self.assertEqual(str(self.blog_post.title), 'Test Blog Post')


class ThreadPostModelTest(TestCase):
    """测试ThreadPost模型"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # 创建测试社团
        self.club = Club.objects.create(
            name='Test Club',
            description='This is a test club'
        )
        
        # 创建测试博客
        self.blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            content='This is a test blog post content.',
            author=self.user,
            club=self.club
        )
        
        # 创建测试讨论
        self.thread_post = ThreadPost.objects.create(
            content='This is a test thread post content.',
            author=self.user,
            blog_post=self.blog_post
        )
    
    def test_thread_post_creation(self):
        """测试讨论是否被正确创建"""
        self.assertEqual(self.thread_post.content, 'This is a test thread post content.')
        self.assertEqual(self.thread_post.author, self.user)
        self.assertEqual(self.thread_post.blog_post, self.blog_post)
        self.assertTrue(self.thread_post.created_at <= timezone.now())


class BlogPostFormTest(TestCase):
    """测试BlogPostForm表单"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # 创建测试社团
        self.club = Club.objects.create(
            name='Test Club',
            description='This is a test club'
        )
        
        # 添加用户为社团成员
        Membership.objects.create(
            user=self.user,
            club=self.club,
            is_manager=True
        )
    
    def test_blog_post_form_valid_data(self):
        """测试表单有效数据"""
        form = BlogPostForm(
            data={
                'title': 'Test Blog Post',
                'content': 'This is a test blog post content.',
                'club': self.club.pk
            },
            user=self.user
        )
        self.assertTrue(form.is_valid())
    
    def test_blog_post_form_invalid_data(self):
        """测试表单无效数据"""
        form = BlogPostForm(
            data={
                'title': '',  # 标题为空
                'content': 'This is a test blog post content.',
                'club': self.club.pk
            },
            user=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class ThreadPostFormTest(TestCase):
    """测试ThreadPostForm表单"""
    
    def test_thread_post_form_valid_data(self):
        """测试表单有效数据"""
        form = ThreadPostForm(
            data={
                'content': 'This is a test thread post content.'
            }
        )
        self.assertTrue(form.is_valid())
    
    def test_thread_post_form_invalid_data(self):
        """测试表单无效数据"""
        form = ThreadPostForm(
            data={
                'content': ''  # 内容为空
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)


class BlogPostViewsTest(TestCase):
    """测试博客文章视图"""
    
    def setUp(self):
        # 创建测试客户端
        self.client = Client()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # 创建测试社团
        self.club = Club.objects.create(
            name='Test Club',
            description='This is a test club'
        )
        
        # 添加用户为社团成员
        Membership.objects.create(
            user=self.user,
            club=self.club,
            is_manager=True
        )
        
        # 创建测试博客
        self.blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            content='This is a test blog post content.',
            author=self.user,
            club=self.club
        )
    
    def test_blog_list_view(self):
        """测试博客列表视图"""
        response = self.client.get(reverse('forum_system:blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogpost_list.html')
        self.assertContains(response, 'Test Blog Post')
    
    def test_blog_detail_view(self):
        """测试博客详情视图"""
        response = self.client.get(reverse('forum_system:blog_detail', args=[self.blog_post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogpost_detail.html')
        self.assertContains(response, 'Test Blog Post')
    
    def test_blog_create_view_unauthenticated(self):
        """测试未登录用户的博客创建视图"""
        response = self.client.get(reverse('forum_system:blog_create'))
        self.assertRedirects(response, f'/login/?next={reverse("forum_system:blog_create")}')
    
    def test_blog_create_view_authenticated(self):
        """测试已登录用户的博客创建视图"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('forum_system:blog_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogpost_form.html')
    
    def test_blog_delete_view(self):
        """测试博客删除视图"""
        self.client.login(username='testuser', password='testpassword')
        # 先确认博客存在
        self.assertTrue(BlogPost.objects.filter(pk=self.blog_post.pk).exists())
        
        # 测试GET请求 - 现在应该重定向到博客列表
        response = self.client.get(reverse('forum_system:blog_delete', args=[self.blog_post.pk]))
        self.assertRedirects(response, reverse('forum_system:blog_list'))
        
        # 测试POST请求 - 实际删除
        response = self.client.post(reverse('forum_system:blog_delete', args=[self.blog_post.pk]))
        self.assertRedirects(response, reverse('forum_system:blog_list'))
        self.assertFalse(BlogPost.objects.filter(pk=self.blog_post.pk).exists())


class ThreadPostViewsTest(TestCase):
    """测试讨论视图"""
    
    def setUp(self):
        # 创建测试客户端
        self.client = Client()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # 创建测试社团
        self.club = Club.objects.create(
            name='Test Club',
            description='This is a test club'
        )
        
        # 创建测试博客
        self.blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            content='This is a test blog post content.',
            author=self.user,
            club=self.club
        )
        
        # 创建测试讨论
        self.thread_post = ThreadPost.objects.create(
            content='This is a test thread post content.',
            author=self.user,
            blog_post=self.blog_post
        )
    
    def test_add_thread_post(self):
        """测试添加讨论"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(
            reverse('forum_system:blog_detail', args=[self.blog_post.pk]),
            {'content': 'This is a new thread post.'}
        )
        self.assertEqual(response.status_code, 302)  # 应该是重定向
        # 检查新讨论是否已添加
        self.assertEqual(ThreadPost.objects.filter(blog_post=self.blog_post).count(), 2)
        self.assertTrue(ThreadPost.objects.filter(content='This is a new thread post.').exists())
    
    def test_delete_thread_post(self):
        """测试删除讨论"""
        self.client.login(username='testuser', password='testpassword')
        # 先确认讨论存在
        self.assertTrue(ThreadPost.objects.filter(pk=self.thread_post.pk).exists())
        
        # 测试GET请求 - 现在应该重定向回博客详情页
        response = self.client.get(reverse('forum_system:threadpost_delete', args=[self.thread_post.pk]))
        self.assertRedirects(response, reverse('forum_system:blog_detail', args=[self.blog_post.pk]))
        
        # 测试POST请求 - 实际删除
        response = self.client.post(reverse('forum_system:threadpost_delete', args=[self.thread_post.pk]))
        self.assertRedirects(response, reverse('forum_system:blog_detail', args=[self.blog_post.pk]))
        self.assertFalse(ThreadPost.objects.filter(pk=self.thread_post.pk).exists())


class BlogListFilterTest(TestCase):
    """测试博客列表筛选功能"""
    
    def setUp(self):
        # 创建测试客户端
        self.client = Client()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
        # 创建两个测试社团
        self.club1 = Club.objects.create(
            name='Test Club 1',
            description='This is test club 1'
        )
        
        self.club2 = Club.objects.create(
            name='Test Club 2',
            description='This is test club 2'
        )
        
        # 创建测试博客
        self.blog_post1 = BlogPost.objects.create(
            title='Test Blog 1',
            content='Content for test blog 1',
            author=self.user,
            club=self.club1
        )
        
        self.blog_post2 = BlogPost.objects.create(
            title='Test Blog 2',
            content='Content for test blog 2',
            author=self.user,
            club=self.club2
        )
    
    def test_filter_by_club(self):
        """测试按社团筛选"""
        response = self.client.get(f"{reverse('forum_system:blog_list')}?club={self.club1.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Blog 1')
        self.assertNotContains(response, 'Test Blog 2')
    
    def test_search_function(self):
        """测试搜索功能"""
        response = self.client.get(f"{reverse('forum_system:blog_list')}?q=Blog 1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Blog 1')
        self.assertNotContains(response, 'Test Blog 2')
    
    def test_sort_order(self):
        """测试排序功能"""
        # 更新博客发布时间使其有明显区别
        self.blog_post1.created_at = timezone.now() - timezone.timedelta(days=1)
        self.blog_post1.save()
        
        # 测试升序排序 (最早的先显示)
        response = self.client.get(f"{reverse('forum_system:blog_list')}?order=asc")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # 检查博客1是否在博客2之前
        pos1 = content.find('Test Blog 1')
        pos2 = content.find('Test Blog 2')
        self.assertTrue(pos1 < pos2)
        
        # 测试降序排序 (最新的先显示)
        response = self.client.get(f"{reverse('forum_system:blog_list')}?order=desc")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # 检查博客2是否在博客1之前
        pos1 = content.find('Test Blog 1')
        pos2 = content.find('Test Blog 2')
        self.assertTrue(pos2 < pos1)
