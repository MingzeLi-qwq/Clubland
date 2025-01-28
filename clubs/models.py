from django.db import models
from users.models import CustomUser  # 引入自定义用户模型

class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='club_logos/', null=True, blank=True)
    leader = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='leader_clubs',
        help_text='The leader of the club.'
    )

    def __str__(self):
        return self.name

class ClubRequest(models.Model):
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='club_requests')
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"Request for {self.name} by {self.applicant.username}"

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='news')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_news')

    def __str__(self):
        return self.title

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_events')

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=[('leader', 'Leader'), ('member', 'Member')], default='member')

    class Meta:
        unique_together = ('user', 'club')

    def __str__(self):
        return f"{self.user.username} in {self.club.name}"
