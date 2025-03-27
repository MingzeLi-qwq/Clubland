import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = "Generate 100 test users"
    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting to generate users...")

        # **Fixed user list**
        fixed_users = [
            {"username": "@admin", "email": "admin@example.com", "first_name": "Admin", "last_name": "User", "account_type": "Admin", "password": "Password123!"},
            {"username": "@john_doe", "email": "john.doe@example.com", "first_name": "John", "last_name": "Doe", "account_type": "User", "password": "Password123!"},
            {"username": "@jane_smith", "email": "jane.smith@example.com", "first_name": "Jane", "last_name": "Smith", "account_type": "User", "password": "Password123!"},
        ]
        
        for user_data in fixed_users:
            if not User.objects.filter(email=user_data["email"]).exists():
                user = User.objects.create(
                    username=user_data["username"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    account_type=user_data["account_type"],
                )
                user.set_password(user_data["password"])
                user.save()
        self.stdout.write("✅ Fixed users created: @admin | @john_doe | @jane_smith")

        # **Randomly generate the remaining users**
        for i in range(97):  # 100 - 3 fixed users
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"@{first_name.lower()}_{last_name.lower()}{random.randint(1, 99)}"
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@example.com"
            account_type = "User"
            password = "Password123!"

            if not User.objects.filter(email=email).exists():
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    account_type=account_type,
                )
                user.set_password(password)
                user.save()

        self.stdout.write("🎉 Successfully generated 100 users!")
