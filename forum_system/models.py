from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()  # 使用 RichTextUploadingField 后台会自动提供富文本编辑功能，支持上传图片
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] 

class Comment(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
