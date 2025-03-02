from django.db import models
from user_system.models import User
from club_system.models import Club  # 引入 Club 模型
from event_system.models import Event  # 新增导入 Event 模型

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class News(TimestampMixin, models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        related_name='news_event'
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        related_name='news'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='newsAuthorship'
    )

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.event:
            self.club = self.event.club
        super().save(*args, **kwargs)

class Comment(TimestampMixin, models.Model):
    news = models.ForeignKey(
        News, 
        on_delete=models.CASCADE, 
        related_name='commentsBelongToNews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commentAuthorship'
    )
