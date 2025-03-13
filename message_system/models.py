from django.db import models
from django.conf import settings  # 引入 settings 以使用自定义用户模型

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')  # 设置 unique related_name
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')  # 设置 unique related_name
    text = models.TextField()

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"
