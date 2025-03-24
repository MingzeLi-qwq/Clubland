from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Delete all test users, except for the superuser."

    def handle(self, *args, **kwargs):
        protected_users = ["superuser@kcl.ac.uk", "@superuser"]
        deleted_count = 0

        users = User.objects.exclude(email__in=protected_users).exclude(username__in=protected_users)

        if users.exists():
            deleted_count = users.count()
            users.delete()
            self.stdout.write(f"Deleted {deleted_count} test users, kept superusers {protected_users}")
        else:
            self.stdout.write("No test users to delete")
