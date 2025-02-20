from django.shortcuts import get_object_or_404, render
from django.views import View
from django.db.models import Q
from user_system.helpers.mixins import LoginRequiredMixin, UserTypeRequiredMixin
from club_system.models import Club, Membership, NewClubRequest
from user_system.models import User


"""-----------------------------------------以下内容负责渲染Admin Panel---------------------------------------------------"""
class AdminPanelClubs(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        if search_query:
            clubs = Club.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
        else:
            clubs = Club.objects.all()
        
        club_count = Club.objects.all().count()
        return render(request, 'admin_panel/clubs.html', {
            'clubs': clubs,
            'club_count': club_count,
            'search_query': search_query,
        })
    
class AdminPanelUsers(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        if search_query:
            users = User.objects.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query),
                account_type=User.ACCOUNT_TYPE_USER
            )
        else:
            users = User.objects.filter(account_type=User.ACCOUNT_TYPE_USER)
        
        user_count = User.objects.all().count()
        return render(request, 'admin_panel/users.html', {
            'users': users,
            'user_count': user_count,
            'search_query': search_query,
        })
    
class AdminPanelEvents(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/events.html')
    
class AdminPanelRequests(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, *args, **kwargs):
        return render(request, 'admin_panel/requests.html')
"""-----------------------------------------以上内容负责渲染Admin Panel---------------------------------------------------"""






"""-----------------------------------------以下内容负责渲染Admin Panel Club---------------------------------------------------"""
class AdminPanelClubsGeneral(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, "admin_panel/admin_panel_club/general.html", {
            'club':club,
            'club_id':club_id,
        })
    
class AdminPanelClubsMembers(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, "admin_panel/admin_panel_club/members.html", {
            'club':club,
            'club_id':club_id,
        })
    
class AdminPanelClubsNews(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, "admin_panel/admin_panel_club/news.html", {
            'club':club,
            'club_id':club_id,
        })
    
class AdminPanelClubsEvents(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        return render(request, "admin_panel/admin_panel_club/events.html", {
            'club':club,
            'club_id':club_id,
        })
"""-----------------------------------------以上内容负责渲染Admin Panel Club---------------------------------------------------"""







"""-----------------------------------------以下内容负责渲染Admin Panel User---------------------------------------------------"""
class AdminPanelUserInformation(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, username, *args, **kwargs):
        panel_user = get_object_or_404(User, username=username)
        return render(request, "admin_panel/admin_panel_user/information.html", {
            'panel_user':panel_user,
            'panel_username':username,
        })

class AdminPanelUserMemberships(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, username, *args, **kwargs):
        panel_user = get_object_or_404(User, username=username)
        return render(request, "admin_panel/admin_panel_user/memberships.html", {
            'panel_user':panel_user,
            'panel_username':username,
        })
    
class AdminPanelUserRequests(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']
    def get(self, request, username, *args, **kwargs):
        panel_user = get_object_or_404(User, username=username)
        return render(request, "admin_panel/admin_panel_user/requests.html", {
            'panel_user':panel_user,
            'username':username,
        })

"""-----------------------------------------以上内容负责渲染Admin Panel User---------------------------------------------------"""
