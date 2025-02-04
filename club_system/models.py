from django.db import models
from user_system.models import User

class Club(models.Model):
    club_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False)  # 从1开始递增的纯数字编号
    name = models.CharField(max_length=50, unique=True, blank=False)  # 社团名称，不能为空，允许空格, 不可以重复
    description = models.CharField(max_length=200, blank=True, null=True)  # 社团简介，最多200字符，可为空
    members = models.ManyToManyField(
        User,
        through='Membership',
        related_name='clubs_joined'
    )

    """This section is used to implement the logic for incrementing association IDs"""
    """此部分用来实现社团ID递增的逻辑"""
    def save(self, *args, **kwargs):
        if not self.club_id:  # 当未分配 club_id 时
            last_club = Club.objects.order_by('-club_id').first()
            if last_club:
                self.club_id = last_club.club_id + 1
            else:
                self.club_id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Club_id:{self.club_id} - {self.name}"
    

"""
The Membership model is used to represent the many-to-many relationship between users and organizations, 
and contains additional fields to store the user's role in the organization and the date of joining.
Membership model用于表现用户和社团间多对多的关系,并包含一些额外的字段来存储用户在社团中的角色和加入日期
"""
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    is_manager = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'club')]  # 确保用户不能重复加入同一社团