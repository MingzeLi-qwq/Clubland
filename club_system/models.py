from django.db import models

class Clubs(models.Model):
    club_id = models.AutoField(primary_key=True) # 主键ID, 从1开始递增
    name = models.CharField(max_length=50, unique=False, blank=False)  # 社团名称，不能为空，允许空格
    description = models.CharField(max_length=200, blank=True, null=True)  # 社团简介，最多200字符，可为空

    def __str__(self):
        return f"Club_id:{self.club_id} - {self.name}"
