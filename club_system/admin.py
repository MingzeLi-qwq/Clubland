from django.contrib import admin
from .models import Club, Membership, NewClubRequest

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('club_id', 'name', 'description')
    search_fields = ('name',)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'is_manager', 'date_joined')
    search_fields = ('user__username', 'club__name')

@admin.register(NewClubRequest)
class NewClubRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('name', 'creator__username', 'description')
    readonly_fields = ('created_at',)
