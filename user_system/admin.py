from django.contrib import admin

# Register your models here.
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'account_type', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')

