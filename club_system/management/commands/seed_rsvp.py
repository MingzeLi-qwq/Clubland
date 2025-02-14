from django.core.management.base import BaseCommand
from user_system.models import User
from event_system.models import Event, RSVP
from club_system.models import Membership
import random

class Command(BaseCommand):
    """Django Management Command to seed RSVP data into the database."""

    help = "Seeds the database with RSVP data"

    def handle(self, *args, **options):
        """Add RSVP records ensuring each Event has at least 4 RSVPs."""
        self.stdout.write("🚀 开始生成 RSVP 记录...")

        events = list(Event.objects.all())  # 获取所有活动

        if not events:
            self.stdout.write(self.style.ERROR("❌ 没有可用的活动，请先添加活动数据！"))
            return

        for event in events:
            existing_rsvp_count = RSVP.objects.filter(event=event).count()

            if existing_rsvp_count >= 4:
                self.stdout.write(self.style.SUCCESS(f"✅ 活动 {event.name} 已有 {existing_rsvp_count} 个 RSVP，跳过..."))
                continue

            # 获取社团成员
            club_members = list(User.objects.filter(membership__club=event.club))

            if not club_members:
                self.stdout.write(self.style.WARNING(f"⚠️ 活动 {event.name} 所属社团 {event.club.name} 没有成员，无法报名！"))
                continue

            required_rsvp = 4 - existing_rsvp_count  # 需要额外添加的 RSVP 数量
            random_users = random.sample(club_members, k=min(len(club_members), required_rsvp))  # 随机选择社团成员

            for user in random_users:
                if not RSVP.objects.filter(user=user, event=event).exists():  # 避免重复 RSVP
                    RSVP.objects.create(user=user, event=event)
                    self.stdout.write(f"📌 {user.username} 预定了 {event.name}（社团 {event.club.name}）")

        self.stdout.write(self.style.SUCCESS("🎉 RSVP 预定数据创建完成！"))
