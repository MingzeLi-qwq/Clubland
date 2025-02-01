from django.db import models

class Club(models.Model):
    club_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False)  # 从1开始递增的纯数字编号
    name = models.CharField(max_length=50, unique=True, blank=False)  # 社团名称，不能为空，允许空格, 不可以重复
    description = models.CharField(max_length=200, blank=True, null=True)  # 社团简介，最多200字符，可为空

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