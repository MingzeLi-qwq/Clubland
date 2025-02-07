from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Club, Membership
from user_system.models import User
from .helpers.mixins import ClubExistsRequiredMixin, NonClubMemberRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, ClubManagerRequiredMixin
from user_system.helpers.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse

"""此方法用来渲染Club列表页"""
"""This method is used to render the Club list page"""
def clubs(request):
    clubs = Club.objects.all()
    return render(request, 'clubs.html', {'clubs': clubs})

"""此方法用于检查Club name是否重复, 更重要的是忽略了大小写和空格"""
"""This method checks for duplicate Club names, and more importantly, ignores case and spaces."""
def isSameClubNameExist(name):
    normalized_name = ''.join(name.split()).lower()
    clubs = Club.objects.all()
    for club in clubs:
        normalized_club_name = ''.join(club.name.split()).lower()
        if normalized_name == normalized_club_name:
            return True
    return False

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
        

"""下面是个方法用于渲染Club Manager页面"""


class ClubManagerGeneral(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)

        return render(request, 'club_manager/general.html', {
            'club_id': club_id,
            'club': club,
        })
    
class ClubManagerMembers(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        managers = club.membership_set.filter(is_manager=True)
        muggles = club.membership_set.filter(is_manager=False)

        return render(request, 'club_manager/members.html', {
            'club_id': club_id,
            'club': club,
            'managers': managers,
            'muggles' : muggles,
            'user': request.user,
        })
    
class ClubManagerNews(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)

        return render(request, 'club_manager/news.html', {
            'club_id': club_id,
            'club': club,
        })
    
class ClubManagerEvents(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)

        return render(request, 'club_manager/events.html', {
            'club_id': club_id,
            'club': club,
        })

"""This method is used to handle name update requests from the manager general."""
"""此方法用于处理来自manager general更新name请求"""
class UpdateClubName(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        new_name = request.POST.get('club_name', '').strip()

        if new_name == club.name:
            messages.error(request, "The new name cannot duplicate the old name.")
            return redirect('club_manager_general', club_id=club_id)

        if not new_name:
            messages.error(request, "Club name cannot be empty.")
            return redirect('club_manager_general', club_id=club_id)
        
        if isSameClubNameExist(new_name):
            messages.error(request, "There's already a Club with the same name.")
            return redirect('club_manager_general', club_id=club_id)
            
        try:
            club.name = new_name
            club.save()
            messages.success(request, "Club name updated successfully.")
        except IntegrityError:
            messages.error(request, "This club name does not match the specification.")
        
        return redirect('club_manager_general', club_id=club_id)

"""This method is used to handle description update requests from the manager general."""
"""此方法用于处理来自manager general更新description请求"""
class UpdateClubDescription(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        new_description = request.POST.get('club_description', '').strip()
        
        if new_description == club.description:
            messages.error(request, "The new description cannot duplicate the old description.")
            return redirect('club_manager_general', club_id=club_id)

        if not new_description:
            new_description = "This Club hasn't added a Description yet"
            messages.success(request, "Empty content will use the default Description")
        
        club.description = new_description
        club.save()
        messages.success(request, "Description updated successfully.")
        
        return redirect('club_manager_general', club_id=club_id)
    

class RemoveManagerView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username):
        club = get_object_or_404(Club, pk=club_id)
        user = get_object_or_404(User, username=username)
        membership = get_object_or_404(Membership, club=club, user=user)

        # 检查是否是最后一个管理员
        if Membership.objects.filter(club=club, is_manager=True).count() <= 1:
            messages.error(request, "At least one manager is required.")
            return redirect('club_manager_members', club_id=club_id)

        # 移除管理员资格
        membership.is_manager = False
        membership.save()
        messages.success(request, f"{user.get_full_name} is no longer a manager.")
        return redirect('club_manager_members', club_id=club_id)
    
class SetManagerView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username):
        club = get_object_or_404(Club, pk=club_id)
        user = get_object_or_404(User, username=username)
        membership = get_object_or_404(Membership, club=club, user=user)

        # 设置为管理员
        membership.is_manager = True
        membership.save()
        messages.success(request, f"{user.get_full_name} is now a manager.")
        return redirect('club_manager_members', club_id=club_id)