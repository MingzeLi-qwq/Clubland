from django.test import TestCase
from django.utils import timezone
from news_system.forms import NewsForm, CommentForm
from news_system.models import News, Comment
from user_system.models import User
from club_system.models import Club, Membership
from event_system.models import Event

class NewsFormTest(TestCase):
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
        
        cls.admin_user = User.objects.create(
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
        
        # 创建另一个测试社团
        cls.another_club = Club.objects.create(
            name="Another Club",
            description="Another Club Description"
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
        
        # 创建另一个社团的活动
        cls.another_event = Event.objects.create(
            name="Another Event",
            club=cls.another_club,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            location="Another Location",
            description="Another Event Description"
        )
    
    def test_news_form_init_for_normal_user(self):
        """测试普通用户初始化表单时只能选择他们管理的社团"""
        form = NewsForm(user=self.user)
        self.assertEqual(form.fields['club'].queryset.count(), 1)
        self.assertEqual(form.fields['club'].queryset.first(), self.club)
    
    def test_news_form_init_for_admin(self):
        """测试管理员初始化表单时可以选择所有社团"""
        form = NewsForm(user=self.admin_user)
        self.assertEqual(form.fields['club'].queryset.count(), 2)
        self.assertFalse(form.fields['club'].required)  # 管理员可以不选择社团
    
    def test_news_form_validation_with_valid_data(self):
        """测试有效数据的表单验证"""
        form_data = {
            'title': 'Test News',
            'club': self.club.pk,
            'event': self.event.pk,
            'content': 'Test Content'
        }
        form = NewsForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_news_form_validation_without_club(self):
        """测试没有选择社团时的表单验证"""
        form_data = {
            'title': 'Test News',
            'content': 'Test Content'
        }
        # 普通用户必须选择社团
        form = NewsForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        
        # 管理员可以不选择社团
        form = NewsForm(data=form_data, user=self.admin_user)
        self.assertTrue(form.is_valid())
    
    def test_news_form_validation_with_event_without_club(self):
        """测试选择活动但没有选择社团时的表单验证"""
        form_data = {
            'title': 'Test News',
            'event': self.event.pk,
            'content': 'Test Content'
        }
        # 普通用户必须选择社团
        form = NewsForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('event', form.errors)
        
        # 管理员不选社团但选择活动时也应该验证失败
        form = NewsForm(data=form_data, user=self.admin_user)
        self.assertFalse(form.is_valid())
        self.assertIn('event', form.errors)
    
    def test_news_form_validation_with_mismatched_club_and_event(self):
        """测试选择的活动不属于所选社团时的表单验证"""
        form_data = {
            'title': 'Test News',
            'club': self.club.pk,
            'event': self.another_event.pk,  # 这个活动不属于选择的社团
            'content': 'Test Content'
        }
        # 当活动和社团不匹配时，表单应该验证失败
        form = NewsForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('event', form.errors)
        
        # 管理员也应该遵循同样的验证规则
        form = NewsForm(data=form_data, user=self.admin_user)
        self.assertFalse(form.is_valid())
        self.assertIn('event', form.errors)
    
    def test_news_form_event_field_initialization(self):
        """测试初始化表单时event字段的设置"""
        # 测试创建新表单时的事件字段（应为空）
        form = NewsForm(user=self.user)
        self.assertEqual(form.fields['event'].queryset.count(), 0)
        
        # 测试修改现有新闻时的事件字段
        news = News.objects.create(
            title="Test News with Event",
            content="Content",
            author=self.user,
            club=self.club,
            event=self.event
        )
        
        # 使用instance参数初始化表单
        form = NewsForm(user=self.user, instance=news)
        # 事件字段应该包含与社团关联的事件
        self.assertEqual(form.fields['event'].queryset.count(), 1)
        self.assertEqual(form.fields['event'].queryset.first(), self.event)


class CommentFormTest(TestCase):
    def test_comment_form_validation_with_valid_data(self):
        """测试有效数据的评论表单验证"""
        form_data = {
            'text': 'Test Comment'
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_comment_form_validation_with_empty_text(self):
        """测试空评论内容的表单验证"""
        form_data = {
            'text': ''
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)