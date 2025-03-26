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
        self.stdout.write("Start generating RSVP records...")

        events = list(Event.objects.all()

        if not events:
            self.stdout.write(self.style.ERROR("There are no available campaigns, please add campaign data first!"))
            return

        for event in events:
            existing_rsvp_count = RSVP.objects.filter(event=event).count()

            if existing_rsvp_count >= 4:
                self.stdout.write(self.style.SUCCESS(f"Event {event.name} Have {existing_rsvp_count} RSVPs..."))
                continue

            club_members = list(User.objects.filter(membership__club=event.club))

            if not club_members:
                self.stdout.write(self.style.WARNING(f"{event.name} belongs to {event.club.name} with no members, skipping..."))
                continue

            required_rsvp = 4 - existing_rsvp_count  # Number of additional RSVPs to be added
            random_users = random.sample(club_members, k=min(len(club_members), required_rsvp))  # Random selection of club members

            for user in random_users:
                if not RSVP.objects.filter(user=user, event=event).exists():  # Avoid duplicate RSVPs
                    RSVP.objects.create(user=user, event=event)
                    self.stdout.write(f"{user.username} participant event: {event.name}（club: {event.club.name}）")

        self.stdout.write(self.style.SUCCESS("seed RSVPs finished！"))
