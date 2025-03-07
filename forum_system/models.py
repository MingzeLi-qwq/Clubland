from django.db import models
from CMS_mixins.CMS_models import TimestampMixin, BasicPost  # 修改为 BasicPost
from user_system.models import User
from club_system.models import Club

class BlogPost(BasicPost):  # 继承 BasicPost
    title = models.CharField(max_length=200)
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogPosts'
    )
    class Meta:
        ordering = ['-created_at']

class ThreadPost(BasicPost):  # 继承 BasicPost
    blog_post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE, 
        related_name='thread_posts'
    )
    # 其它字段从 BasicPost 中已包含
