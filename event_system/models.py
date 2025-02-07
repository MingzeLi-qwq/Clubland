from django.db import models
from club_system.models import Club
from user_system.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)  
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category)
    description = models.TextField()
    participants = models.ManyToManyField(User, blank=True, related_name='events_joined')
    is_featured = models.BooleanField(default=False) #to show in home page 用于主页展示

    def __str__(self):
        return f"{self.name} by {self.club.name}"

#用户报名模型记录 to record users registed every event
class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'event')
