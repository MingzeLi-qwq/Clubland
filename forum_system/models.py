from django.db import models
from user_system.models import User
from ckeditor_uploader.fields import RichTextUploadingField

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class BlogPost(TimestampMixin, models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
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
    # 直接使用 ForeignKey 表示每条评论只有一个作者
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commentAuthorship'
    )
