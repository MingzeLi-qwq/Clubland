from django.db import models
from user_system.models import User
from club_system.models import Club  # 引入 Club 模型

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class BlogPost(TimestampMixin, models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogPosts'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogPostAuthorship'
    )

    class Meta:
        ordering = ['-created_at']

# 将 Comment 模型重命名为 ThreadPost
class ThreadPost(TimestampMixin, models.Model):
    blog_post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE, 
        related_name='thread_posts'
    )
    # 将 text 字段重命名为 content
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='forumThreadPostAuthorship'
    )
