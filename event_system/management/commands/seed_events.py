from django.core.management.base import BaseCommand
from club_system.models import Club
from user_system.models import User
from event_system.models import Event
from django.utils import timezone

class Command(BaseCommand):
    help = '生成活动测试数据'

    def handle(self, *args, **options):
        # 获取现有的社团
        coding_club = Club.objects.get(name="Coding Club")  # 确保社团名称匹配

        Event.objects.create(
            name="Python新手训练营",
            club=coding_club,
            start_time=timezone.now() + timezone.timedelta(days=3),
            location="实验楼302",
            description="零基础Python入门课程"
        )

        self.stdout.write(self.style.SUCCESS('成功生成活动数据'))
