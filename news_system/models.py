from django.db import models
from CMS_mixins.models import TimestampMixin, AuthorshipMixin, BasicPost  # 修改为 BasicPost
from user_system.models import User
from club_system.models import Club
from event_system.models import Event

class News(BasicPost):  # 改为继承 BasicPost
    title = models.CharField(max_length=200)
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
    # author 和 content 已由 BasicPost 包含

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.event:
            self.club = self.event.club
        super().save(*args, **kwargs)

class Comment(TimestampMixin, AuthorshipMixin, models.Model):
    news = models.ForeignKey(
        News, 
        on_delete=models.CASCADE, 
        related_name='newsComments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
