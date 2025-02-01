from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "删除所有测试用户，除了后台用户Superuser"

    def handle(self, *args, **kwargs):
        protected_users = ["superuser@kcl.ac.uk", "@superuser"]
        deleted_count = 0

        users = User.objects.exclude(email__in=protected_users).exclude(username__in=protected_users)

        if users.exists():
            deleted_count = users.count()
            users.delete()
            self.stdout.write(f"🗑️ 已删除 {deleted_count} 个测试用户，保留超级用户 {protected_users}")
        else:
            self.stdout.write("✅ 没有需要删除的测试用户")
