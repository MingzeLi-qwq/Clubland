# event_system/management/commands/unseed_events.py
from django.core.management.base import BaseCommand
from club_system.models import Club
from event_system.models import Event

class Command(BaseCommand):
    help = '删除通过 seed_events 创建的测试数据'

    def handle(self, *args, **options):
        try:
            # 1. 查找目标社团
            coding_club = Club.objects.get(name="Coding Club")
            
            # 2. 删除关联活动
            deleted_count, _ = Event.objects.filter(
                name="Python新手训练营",
                club=coding_club
            ).delete()

            # 3. 输出结果
            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'成功删除 {deleted_count} 个活动')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('未找到匹配的测试活动')
                )

        except Club.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('未找到 "Coding Club" 社团')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'删除失败: {str(e)}')
            )