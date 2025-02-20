from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.db.models import Q
from user_system.helpers.mixins import LoginRequiredMixin, UserTypeRequiredMixin
from club_system.models import Club, Membership, NewClubRequest
from user_system.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse


def verifyAdminPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            # 密码验证成功
            request.session['password_verified'] = True
            if request.session.get('pending_action') == 'delete_club':
                club_id = request.session.get('club_id')
                return redirect('admin_delete_club', club_id=club_id)
            return redirect(request.session.get('return_url', 'admin_panel_clubs'))
        else:
            messages.error(request, 'Wrong password, please try again.')
    
    return render(request, 'verify_password.html')


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
        search_query = request.GET.get('search', '')
        
        pending_requests = NewClubRequest.objects.filter(status='pending')
        finished_requests = NewClubRequest.objects.filter(Q(status='approved') | Q(status='rejected'))
        
        if search_query:
            pending_requests = pending_requests.filter(name__icontains=search_query)
            finished_requests = finished_requests.filter(name__icontains=search_query)
        
        context = {
            'search_query': search_query,
            'pending_requests': pending_requests,
            'finished_requests': finished_requests,
            'pending_count': pending_requests.count(),
            'finished_count': finished_requests.count(),
        }
        
        return render(request, 'admin_panel/requests.html', context)
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
        managers = club.membership_set.filter(is_manager=True)
        manager_count = managers.count()
        muggles = club.membership_set.filter(is_manager=False)
        muggle_count = muggles.count()

        return render(request, "admin_panel/admin_panel_club/members.html", {
            'club_id': club_id,
            'club': club,
            'managers': managers,
            'muggles' : muggles,
            'manager_count': manager_count,
            'muggle_count': muggle_count
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
    

# 以下内容负责处理删除club的请求
class AdminDeleteClub(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['Admin']

    def get(self, request, club_id):
        if request.session.get('password_verified'):
            del request.session['password_verified']
            club = get_object_or_404(Club, pk=club_id)
            club_name = club.name
            club.delete()
            messages.success(request, f"Club '{club_name}' has been deleted")
            return redirect('admin_panel_clubs')
        else:
            return redirect('verify_admin_password')

    def post(self, request, club_id):
        if not request.session.get('password_verified'):
            request.session['return_url'] = reverse('admin_panel_club_general', kwargs={'club_id': club_id})
            request.session['pending_action'] = 'delete_club'
            request.session['club_id'] = club_id
            return redirect('verify_admin_password')
        else:
            return self.get(request, club_id)
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
