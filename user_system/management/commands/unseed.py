from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = "Deletes all seeded data in reverse order"

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.WARNING("🗑 Removing all seeded data..."))

            # call_command("unseed_events")
            # self.stdout.write(self.style.SUCCESS("✅ Events removed successfully!"))

            call_command("unseed_members")
            self.stdout.write(self.style.SUCCESS("✅ Members removed successfully!"))

            call_command("unseed_clubs")
            self.stdout.write(self.style.SUCCESS("✅ Clubs removed successfully!"))

            call_command("unseed_users")
            self.stdout.write(self.style.SUCCESS("✅ Users removed successfully!"))

            call_command("unseed_events")
            self.stdout.write(self.style.SUCCESS("✅ Users removed successfully!"))

            call_command("unseed_rsvp")
            self.stdout.write(self.style.SUCCESS("✅ RSVP removed successfully!"))

            call_command("unseed_news")
            self.stdout.write(self.style.SUCCESS("✅ News removed successfully!"))

            call_command("unseed_blogposts")
            self.stdout.write(self.style.SUCCESS("✅ BlogPosts removed successfully!"))

            self.stdout.write(self.style.SUCCESS("🎉 All unseeding operations completed!"))

        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {e}"))