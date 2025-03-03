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
    # 将 category 字段重命名为 club
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

class Comment(TimestampMixin, models.Model):
    blog_post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE, 
        related_name='commentsBelongToPost'
    )
    text = models.TextField()
    # 修改 related_name 防止与其他应用冲突
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='forumCommentAuthorship'
    )
