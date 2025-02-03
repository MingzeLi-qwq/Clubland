from django.contrib import admin
from .models import Club, Membership

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('club_id', 'name', 'description')
    search_fields = ('name',)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'is_admin', 'date_joined')
    search_fields = ('user__username', 'club__name')
