from django.db import models
from django.conf import settings

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

class AuthorshipMixin(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_authorship"
    )
    class Meta:
        abstract = True

class BasePost(AuthorshipMixin, TimestampMixin, models.Model):
    content = models.TextField()
    class Meta:
        abstract = True
