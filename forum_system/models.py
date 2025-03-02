from django.db import models
from user_system.models import User
from club_system.models import Club  # 引入 Club 模型
from event_system.models import Event  # 新增导入 Event 模型

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class BlogPost(TimestampMixin, models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogPosts_event'
    )
    # 修改: 将 category 字段重命名为 club
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogPosts'
    )

    # 直接使用 ForeignKey 表示每篇文章只有一个作者
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogPostAuthorship'
    )

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # 如果 event 字段不为空，则自动将 category 设为 event 所属的社团
        if self.event:
            # 修改: 将 category 替换为 club
            self.club = self.event.club
        super().save(*args, **kwargs)

class Comment(TimestampMixin, models.Model):
    blog_post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE, 
        related_name='commentsBelongToPost'
    )
    text = models.TextField()
    # 直接使用 ForeignKey 表示每条评论只有一个作者
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commentAuthorship'
    )
