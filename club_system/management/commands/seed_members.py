import random
from django.core.management.base import BaseCommand
from club_system.models import Club, Membership
from user_system.models import User
from faker import Faker


class Command(BaseCommand):
    help = 'Assigning members to Clubs. / 为Clubs分配成员'


    def assign_members(self):
        '''To ensure that the member-user relationship makes sense, I'll delete the existing member relationship before attempting to repeat assign member each time.'''
        '''为了保证member与user关系的合理性, 我会在每次试图重复assign member之前删除已有的member关系'''
        Membership.objects.all().delete()

        for club in self.clubs:
            # 随机挑 40 个用户
            selected_users = random.sample(self.all_regular_users, 40)

            # 将前 2 个用户设置为管理员
            for i, user in enumerate(selected_users):
                # 检查是否已经存在相同的 user_id 和 club_id 组合
                if not Membership.objects.filter(user=user, club=club).exists():
                    Membership.objects.create(
                        user=user,
                        club=club,
                        is_manager=(i < 2)  # 索引 0 和 1 为管理员
                    )

            self.stdout.write("Club member assignments are complete! / Club 成员分配完成！")
    

    def handle(self, *args, **kwargs):
        self.all_regular_users = list(User.objects.filter(account_type='User'))

        self.clubs = list(Club.objects.all())

        if len(self.all_regular_users) < 50:   
            self.stdout.write("Less than 50 available users, can not complete the random allocation! / 可用用户不足 50 人，无法完成随机分配！")
            self.stdout.write("Please use the 'python3 manage.py seed_users' command first. / 请先使用'python3 manage.py seed_users'指令")
            return
        
        if len(self.clubs) < 1:
            self.stdout.write("No available users, can not complete the random allocation! / 没有可用club无法完成随机分配！")
            self.stdout.write("Please use the 'python3 manage.py seed_clubs' command first. / 请先使用'python3 manage.py seed_clubs'指令")
            return

        self.assign_members()