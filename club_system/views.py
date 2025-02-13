from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from .models import Club, Membership
from user_system.models import User
from .helpers.mixins import ClubExistsRequiredMixin, NonClubMemberRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, ClubManagerRequiredMixin
from user_system.helpers.mixins import LoginRequiredMixin
from event_system.models import Event, RSVP
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
import urllib.parse
import json

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


class ClubWebView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubMemberRequiredMixin, View):
    template_name = 'club_website/club_dashboard.html'

    def get(self, request, club_id):
        club = get_object_or_404(Club, club_id=club_id)
        
        # 验证用户是否是该 club 的成员
        if not Membership.objects.filter(club=club, user=request.user, club__isnull=False).exists():
            return render(request, '403.html', status=403)

        membership = Membership.objects.get(club=club, user=request.user)

        return render(request, self.template_name, {
            'club': club,
            'widgets': club.widgets.all(),
            'customization': club.customization,
            'membership': membership
        })
        

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

"""This method is used to handle name update requests from the manager general."""
"""此方法用于处理来自manager general更新club name请求"""
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
"""此方法用于处理来自manager general更新club description请求"""
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
    
"""此部分用于处理来自club manager 移除 manager的请求"""
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
    
    """此部分用于处理来自club manager 新增 manager的请求"""
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
class ClubManagerEvents(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        # 获取当前用户管理的社团
        clubs_managed = Club.objects.filter(membership__user=request.user, membership__is_manager=True)

        # 获取这些社团的活动
        events = Event.objects.filter(club__in=clubs_managed)

        # 终端调试

        return render(request, 'club_manager/club_manager_events.html', {
            'club_id': club_id,
            'club': club,
            'events': events
        })

class EventRSVPListView(LoginRequiredMixin, View):
    """ 获取某活动的 RSVP 成员 """
    def get(self, request, event_id, *args, **kwargs):
        try:
            event = get_object_or_404(Event, pk=event_id)
            rsvp_members = RSVP.objects.filter(event=event).select_related("user")
            members_data = [
            {
                "email": rsvp.user.email,
                "username": rsvp.user.username
            }
            for rsvp in rsvp_members
        ]
            return JsonResponse({"status": "success", "members": members_data, "event_id": event_id})
        
        except Exception as e:
            print(f" {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

class RemoveRSVPView(LoginRequiredMixin, View):
    """ 管理员通过 username 移除 RSVP """

    def post(self, request, event_id, username, *args, **kwargs):
        username = urllib.parse.unquote(username)


        event = get_object_or_404(Event, pk=event_id)
        user = get_object_or_404(User, username=username)
        rsvp = RSVP.objects.filter(event=event, user=user).first()

        if not rsvp:
            return JsonResponse({"status": "error", "message": "RSVP record not found"}, status=404)

        rsvp.delete()
        return JsonResponse({"status": "success", "message": "RSVP removed successfully"})
class AddRSVPView(LoginRequiredMixin, View):
    """ 管理员添加 RSVP """

    def post(self, request, event_id, username, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)
        user = get_object_or_404(User, username=username)

        if RSVP.objects.filter(event=event, user=user).exists():
            return JsonResponse({"status": "error", "message": "User already RSVP'd"}, status=400)

        RSVP.objects.create(event=event, user=user, status=True)

        return JsonResponse({"status": "success", "message": "User RSVP'd"})



