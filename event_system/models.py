from django.db import models
from club_system.models import Club
from user_system.models import User

class Event(models.Model):
    name = models.CharField(max_length=200, unique=True, primary_key=True)  # 按需求设置主键
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    start_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()
    participants = models.ManyToManyField(User, blank=True, related_name='events_joined')

    def __str__(self):
        return f"{self.name} by {self.club.name}"
# Create your models here.
