import random
from django.core.management.base import BaseCommand
from club_system.models import Club, Membership
from user_system.models import User
from faker import Faker


class Command(BaseCommand):
    help = 'Assigning members to Clubs.'


    def assign_members(self):
        '''To ensure that the member-user relationship makes sense, delete the existing member relationship before attempting to repeat assign member each time.'''
        Membership.objects.all().delete()

        for club in self.clubs:
            # 40 randomly selected users
            selected_users = random.sample(self.all_regular_users, 40)

            # Set the first 2 users as administrators
            for i, user in enumerate(selected_users):
                # Check if the same user_id and club_id combination already exists
                if not Membership.objects.filter(user=user, club=club).exists():
                    Membership.objects.create(
                        user=user,
                        club=club,
                        is_manager=(i < 2)
                    )

            self.stdout.write("Club member assignments are complete!")


        # Set up the @john_doe user as an administrator for Book Club
        john_doe = User.objects.get(username='@john_doe')
        book_club = Club.objects.get(name='Book Club')
        membership, created = Membership.objects.get_or_create(user=john_doe, club=book_club)
        if created or not membership.is_manager:
            membership.is_manager = True
            membership.save()
            self.stdout.write("Assigned @john_doe as manager of Book Club.")


    

    def handle(self, *args, **kwargs):
        self.all_regular_users = list(User.objects.filter(account_type='User'))

        self.clubs = list(Club.objects.all())

        if len(self.all_regular_users) < 50:   
            self.stdout.write("Less than 50 available users, can not complete the random allocation! ")
            self.stdout.write("Please use the 'python3 manage.py seed_users' command first. ")
            return
        
        if len(self.clubs) < 1:
            self.stdout.write("No available users, can not complete the random allocation! ")
            self.stdout.write("Please use the 'python3 manage.py seed_clubs' command first. ")
            return

        self.assign_members()