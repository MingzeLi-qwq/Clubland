from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = "Runs all seed scripts in order"

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.SUCCESS("🌱 Seeding data..."))

            call_command("seed_users")
            self.stdout.write(self.style.SUCCESS("✅ Users seeded successfully!"))

            call_command("seed_clubs")
            self.stdout.write(self.style.SUCCESS("✅ Clubs seeded successfully!"))

            call_command("seed_members")
            self.stdout.write(self.style.SUCCESS("✅ Members seeded successfully!"))

            call_command("seed_events")
            self.stdout.write(self.style.SUCCESS("✅ Events seeded successfully!"))

            call_command("seed_rsvp")
            self.stdout.write(self.style.SUCCESS("✅ RSVP seeded successfully!"))

            call_command("seed_news")
            self.stdout.write(self.style.SUCCESS("✅ News seeded successfully!"))

            self.stdout.write(self.style.SUCCESS("🎉 All seeding operations completed!"))

        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {e}"))