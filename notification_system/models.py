from django.db import models
from django.conf import settings 

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('general', 'General Messages'),
        ('approval', 'Club Approval'),
        ('event', 'Event Reminder'),
        ('news', 'News Update'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='general')
    url = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return f"[{self.get_notification_type_display()}] Notification for {self.user.username}: {self.message}"
    
    def save(self, *args, **kwargs):
        # 先保存新通知
        super().save(*args, **kwargs)
        
        # 檢查該用戶的通知總數
        user_notifications = Notification.objects.filter(user=self.user)
        if user_notifications.count() > 2000:
            # 找到最舊的通知並刪除
            oldest = user_notifications.order_by('created_at').first()
            if oldest:
                oldest.delete()

