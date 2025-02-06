from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Club, Membership
from .helpers.mixins import ClubExistsRequiredMixin, NonClubMemberRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin
from user_system.helpers.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

"""此方法用来渲染Club列表页"""
"""This method is used to render the Club list page"""
def clubs(request):
    clubs = Club.objects.all()
    return render(request, 'clubs.html', {'clubs': clubs})

"""此方法用来渲染Club详情页"""
"""This method is used to render the Club details page"""
class ClubDetailView(ClubExistsRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        member_count = club.members.count()
        managers = club.membership_set.filter(is_manager=True)
        is_manager = False
        if request.user.is_authenticated:
            is_manager = managers.filter(user=request.user).exists()
        return render(request, 'club_detail.html', {
            'club': club,
            'member_count': member_count,
            'managers': managers,
            'is_manager': is_manager
        })
    
"""此方法用来处理注册会员请求"""
"""This method is used to handle member registration requests"""
class RegisterMembershipView(LoginRequiredMixin, ClubExistsRequiredMixin, NonClubMemberRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        if request.user.is_authenticated:
            Membership.objects.get_or_create(user=request.user, club=club)
            return redirect('club_detail', club_id=club_id)
        else:
            return redirect('login')
        
"""此方法用来处理取消会员请求"""
""""This method is used to handle membership cancelation requests"""
class CancelMembershipView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        if request.user.is_authenticated:
            Membership.objects.filter(user=request.user, club=club).delete()
            return redirect('club_detail', club_id=club_id)
        else:
            return redirect('login')
        

def clubDashboard(request):
    return render(request, 'club_dashboard.html')