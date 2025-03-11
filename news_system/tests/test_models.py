from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from news_system.models import News, Comment
from user_system.models import User
from club_system.models import Club
from event_system.models import Event

class NewsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 创建测试用户
        cls.user = User.objects.create(
            username="@testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            account_type="User",
            password="testpassword"
        )
        
        # 创建测试社团
        cls.club = Club.objects.create(
            name="Test Club",
            description="Test Club Description"
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
        
        # 创建测试新闻（带活动）
        cls.news_with_event = News.objects.create(
            title="Test News With Event",
            content="Test News Content With Event",
            author=cls.user,
            event=cls.event
        )
    
    def test_news_creation(self):
        """测试新闻创建"""
        self.assertEqual(self.news.title, "Test News")
        self.assertEqual(self.news.content, "Test News Content")
        self.assertEqual(self.news.author, self.user)
        self.assertEqual(self.news.club, self.club)
        self.assertIsNone(self.news.event)
    
    def test_news_with_event_creation(self):
        """测试带活动的新闻创建"""
        self.assertEqual(self.news_with_event.title, "Test News With Event")
        self.assertEqual(self.news_with_event.content, "Test News Content With Event")
        self.assertEqual(self.news_with_event.author, self.user)
        self.assertEqual(self.news_with_event.event, self.event)
        # 测试自动设置club字段
        self.assertEqual(self.news_with_event.club, self.club)
    
    def test_news_str_method(self):
        """测试新闻的字符串表示"""
        # 由于News模型没有定义__str__方法，它会使用默认的对象表示
        # 这里我们只是确保它不会引发错误
        self.assertTrue(str(self.news))
    
    def test_news_ordering(self):
        """测试新闻的排序"""
        # 创建一个新的新闻，确保它的created_at晚于之前创建的新闻
        new_news = News.objects.create(
            title="New Test News",
            content="New Test News Content",
            author=self.user,
            club=self.club
        )
        
        # 获取所有新闻并检查顺序（应该是按created_at降序）
        all_news = News.objects.all()
        self.assertEqual(all_news[0], new_news)  # 最新的新闻应该在最前面

class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 创建测试用户
        cls.user = User.objects.create(
            username="@testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            account_type="User",
            password="testpassword"
        )
        
        # 创建测试社团
        cls.club = Club.objects.create(
            name="Test Club",
            description="Test Club Description"
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
    
    def test_comment_creation(self):
        """测试评论创建"""
        self.assertEqual(self.comment.text, "Test Comment")
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.news, self.news)
    
    def test_comment_str_method(self):
        """测试评论的字符串表示"""
        # 由于Comment模型没有定义__str__方法，它会使用默认的对象表示
        # 这里我们只是确保它不会引发错误
        self.assertTrue(str(self.comment))
    
    def test_comment_news_relationship(self):
        """测试评论与新闻的关系"""
        # 测试从新闻获取评论
        self.assertEqual(self.news.newsComments.count(), 1)
        self.assertEqual(self.news.newsComments.first(), self.comment)
        
        # 测试删除新闻时评论也会被删除（级联删除）
        news_id = self.news.id
        self.news.delete()
        self.assertEqual(Comment.objects.filter(news_id=news_id).count(), 0)