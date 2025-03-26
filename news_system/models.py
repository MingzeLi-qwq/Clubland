from django.db import models
from CMS_mixins.CMS_models import TimestampMixin, AuthorshipMixin, BasicPost
from user_system.models import User
from club_system.models import Club
from event_system.models import Event

class News(BasicPost):
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
