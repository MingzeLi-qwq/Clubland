from django.db import models
from user_system.models import User
from club_system.models import Club

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

# 新建抽象基类，用于封装 content 和 author 的共性
class BasePost(TimestampMixin, models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_authorship"
    )
    class Meta:
        abstract = True

class BlogPost(BasePost):
    title = models.CharField(max_length=200)
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogPosts'
    )
    class Meta:
        ordering = ['-created_at']

class ThreadPost(BasePost):
    blog_post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE, 
        related_name='thread_posts'
    )
    # 其他字段使用 BasePost 中定义的 content 与 author
