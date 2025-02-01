from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    ACCOUNT_TYPE_USER = 'User'
    ACCOUNT_TYPE_ADMIN = 'Admin'

    ACCOUNT_TYPE_CHOICES = [(ACCOUNT_TYPE_USER, 'User'),(ACCOUNT_TYPE_ADMIN, 'Admin')]

    account_type = models.CharField(max_length=20, blank=False, null=False, choices=ACCOUNT_TYPE_CHOICES)
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(unique=True, blank=False, primary_key=True)

    @property
    def is_admin(self):
        return self.account_type == self.ACCOUNT_TYPE_ADMIN
    @property
    def is_user(self):
        return self.account_type == self.ACCOUNT_TYPE_USER
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return (
                f"Username: {self.username}, "
                f"First Name: {self.first_name}, "
                f"Last Name: {self.last_name}, "
                f"Email: {self.email}, "
                f"Account Type: {self.account_type}"
                )