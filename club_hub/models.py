from django.db import models
from club_system.models import Club
from django.contrib.auth import get_user_model

User = get_user_model()

class Widget(models.Model):
    """可拖拽组件"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="widgets")
    name = models.CharField(max_length=100)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    data = models.JSONField(default=dict)  # 组件数据

    def __str__(self):
        return f"{self.name} - {self.club.name}"
