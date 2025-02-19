from django.shortcuts import render
from django.views import View
from django.db.models import Q
from user_system.helpers.mixins import LoginRequiredMixin, UserTypeRequiredMixin
from club_system.models import Club, Membership, NewClubRequest
from user_system.models import User


"""以下内容负责渲染Admin Panel"""
class AdminPanelClubs(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        if search_query:
            clubs = Club.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
        else:
            clubs = Club.objects.all()
        
        club_count = clubs.count()
        return render(request, 'admin_panel/clubs.html', {
            'clubs': clubs,
            'club_count': club_count,
            'search_query': search_query,
        })
    
class AdminPanelUsers(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/users.html')
    
class AdminPanelEvents(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/events.html')
    
class AdminPanelRequests(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/requests.html')