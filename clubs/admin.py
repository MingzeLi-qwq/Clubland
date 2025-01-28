from django.contrib import admin
from django.db import transaction
from .models import Club, News, Event, Membership, ClubRequest

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'description')
    search_fields = ('name',)
    list_filter = ('leader',)

@admin.register(ClubRequest)
class ClubRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'applicant', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    actions = ['approve_request', 'reject_request']

    def approve_request(self, request, queryset):
        """批量批准社团创建申请"""
        with transaction.atomic():
            for club_request in queryset.filter(status='pending'):
                club = Club.objects.create(
                    name=club_request.name,
                    description=club_request.description,
                    leader=club_request.applicant
                )
                # 将申请人加入 Membership 并设为团长
                Membership.objects.create(
                    user=club_request.applicant,
                    club=club,
                    role='leader'
                )
                club_request.status = 'approved'
                club_request.save()

    def reject_request(self, request, queryset):
        """批量拒绝社团创建申请"""
        queryset.filter(status='pending').update(status='rejected')

    approve_request.short_description = "Approve selected requests"
    reject_request.short_description = "Reject selected requests"



@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'role')
    search_fields = ('user__username', 'club__name')
    list_filter = ('role',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'created_at', 'created_by')
    search_fields = ('title',)
    list_filter = ('club', 'created_at')

    def get_queryset(self, request):
        """限制团长只能管理自己社团的新闻"""
        qs = super().get_queryset(request)
        if request.user.role == 'club_leader':
            return qs.filter(club__leader=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        """确保创建者是当前用户"""
        if not obj.pk:  # 创建时
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'club', 'date', 'created_by')
    search_fields = ('name',)
    list_filter = ('club', 'date')

    def get_queryset(self, request):
        """限制团长只能管理自己社团的活动"""
        qs = super().get_queryset(request)
        if request.user.role == 'club_leader':
            return qs.filter(club__leader=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        """确保创建者是当前用户"""
        if not obj.pk:  # 创建时
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
