from django.contrib import admin
from .models import RSVP, Category, Event  # Import Event model

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'club', 'start_time', 'location')  # Fields to display in list view
    search_fields = ('name', 'location')  # Searchable fields
    filter_horizontal = ('participants',)  # Better management for many-to-many fields

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'timestamp')
admin.site.register(Category)