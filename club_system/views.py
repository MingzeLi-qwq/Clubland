from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from .models import Club, Membership, NewClubRequest
from user_system.models import User
from .helpers.mixins import ClubExistsRequiredMixin, NonClubMemberRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, ClubManagerRequiredMixin
from user_system.helpers.mixins import LoginRequiredMixin, UserTypeRequiredMixin
from event_system.models import Event, RSVP, Category
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from club_system.helpers.mixins import ClubExistsRequiredMixin, ClubManagerRequiredMixin
from .forms import NewClubRequestForm
from django.utils import timezone
from notification_system.models import Notification

import urllib.parse
import json

"""------------------------------------------------------Checks if a string is a duplicate of an existing club name.---------------------------------------------------------"""
"""This method is used to render the Club list page"""
"""此方法用来渲染Club列表页"""
def clubs(request):
    search_query = request.GET.get('search', '')
    if search_query:
        clubs = Club.objects.filter(name__icontains=search_query)
    else:
        clubs = Club.objects.all()
    return render(request, 'clubs.html', {
        'clubs': clubs,
        'search_query': search_query
    })


"""This method checks for duplicate Club names, and more importantly, ignores case and spaces."""
"""此方法用于检查Club name是否重复, 更重要的是忽略了大小写和空格"""
def isSameClubNameExist(name):
    normalized_name = ''.join(name.split()).lower()
    clubs = Club.objects.all()
    for club in clubs:
        normalized_club_name = ''.join(club.name.split()).lower()
        if normalized_name == normalized_club_name:
            return True
    return False

def isSameClubNameExistInRequest(name):
    normalized_name = ''.join(name.split()).lower()
    requests = NewClubRequest.objects.all()
    for request in requests:
        normalized_request_name = ''.join(request.name.split()).lower()
        if normalized_name == normalized_request_name:
            return True
    return False

"""--------------------------------------------------------------------------------End-------------------------------------------------------------------------------"""


"""--------------------------------------------------------------------Club Details Page-------------------------------------------------------------------------------"""
"""This method is used to render the Club details page"""
"""此方法用来渲染Club详情页"""
class ClubDetailView(ClubExistsRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        events = Event.objects.filter(club=club)
        member_count = club.members.count()
        managers = club.membership_set.filter(is_manager=True)
        is_manager = False
        if request.user.is_authenticated:
            is_manager = managers.filter(user=request.user).exists()
        return render(request, 'club_detail.html', {
            'club': club,
            'member_count': member_count,
            'managers': managers,
            'is_manager': is_manager,
            'events': events,
        })
    
"""This method is used to handle member registration from user itself"""
"""此方法用来处理来自用户的注册会员"""
class RegisterMembershipView(LoginRequiredMixin, ClubExistsRequiredMixin, UserTypeRequiredMixin, NonClubMemberRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        if request.user.is_authenticated:
            Membership.objects.get_or_create(user=request.user, club=club)
            return redirect('club_detail', club_id=club_id)
        else:
            return redirect('login')
        
""""This method is used to handle membership cancelation from user it self"""
"""此方法用来处理来自用户自己的取消会员"""
class CancelMembershipView(LoginRequiredMixin, ClubExistsRequiredMixin, UserTypeRequiredMixin, ClubMemberRequiredMixin, NonClubManagerRequiredMixin, View):
    allowed_types = ['User']

    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)
        if request.user.is_authenticated:
            Membership.objects.filter(user=request.user, club=club).delete()
            messages.success(request, f"You have successfully cancelled your membership in {club.name}.")
            return redirect('dashboard_my_club')
        else:
            return redirect('login')
"""------------------------------------------------------------------------End-------------------------------------------------------------------------------"""


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
        


"""---------------------------------------------------Club Manager Side Bar------------------------------------------------------------"""
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
        
        # Get search parameters
        manager_search = request.GET.get('manager_search', '')
        member_search = request.GET.get('member_search', '')
        
        # Manager Enquiries
        managers = club.membership_set.filter(is_manager=True)
        if manager_search:
            managers = managers.filter(
                Q(user__first_name__icontains=manager_search) |
                Q(user__last_name__icontains=manager_search) |
                Q(user__email__icontains=manager_search)
            )
        
        # Members Enquiries
        muggles = club.membership_set.filter(is_manager=False)
        if member_search:
            muggles = muggles.filter(
                Q(user__first_name__icontains=member_search) |
                Q(user__last_name__icontains=member_search) |
                Q(user__email__icontains=member_search)
            )
        
        return render(request, 'club_manager/members.html', {
            'club_id': club_id,
            'club': club,
            'managers': managers,
            'muggles': muggles,
            'user': request.user,
            'manager_count': managers.count(),
            'muggle_count': muggles.count(),
            'manager_search_query': manager_search,
            'member_search_query': member_search,
        })
    
class ClubManagerNews(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = Club.objects.get(pk=club_id)

        return render(request, 'club_manager/news.html', {
            'club_id': club_id,
            'club': club,
        })
    
class ClubManagerEvents(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, *args, **kwargs):
        club = get_object_or_404(Club, club_id=club_id)
        search_query = request.GET.get('search', '')
        events = Event.objects.filter(club=club)

        if search_query:
            events = events.filter(
                Q(name__icontains=search_query) |
                Q(start_time__icontains=search_query)
            )

        events = events.order_by('start_time')

        context = {
            'club': club,
            'events': events,
            'club_id': club_id,
            'search_query': search_query,
        }
        return render(request, 'club_manager/events.html', context)
"""------------------------------------------------------------End--------------------------------------------------------------"""



"""----------------------------------------------------------------Club Manager General-------------------------------------------------------------------"""
"""This method is used to handle name update requests from the club manager general and admin panel."""
"""此方法用于处理来自club manager general, admin panel更新club name请求"""
class UpdateClubName(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        new_name = request.POST.get('club_name', '').strip()

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        # 如果访问此view的请求是来自admin panel的, 重新定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_general'
        else:
            redirect_url = 'club_manager_general'

        if new_name == club.name:
            messages.error(request, "The new name cannot duplicate the old name.")
            return redirect(redirect_url, club_id=club_id)

        if not new_name:
            messages.error(request, "Club name cannot be empty.")
            return redirect(redirect_url, club_id=club_id)
        
        if isSameClubNameExist(new_name):
            messages.error(request, "There's already a Club with the same name.")
            return redirect(redirect_url, club_id=club_id)
        
        if isSameClubNameExistInRequest(new_name):
            messages.error(request, "There's already a New Club Request with the same name.")
            return redirect(redirect_url, club_id=club_id)
            
        try:
            club.name = new_name
            club.save()
            messages.success(request, "Club name updated successfully.")
        except IntegrityError:
            messages.error(request, "This club name does not match the specification.")
        
        return redirect(redirect_url, club_id=club_id)

"""This method is used to handle description update requests from the club manager general and admin panel."""
"""此方法用于处理来自club manager general, admin panel更新club description请求"""
class UpdateClubDescription(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        new_description = request.POST.get('club_description', '').strip()

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        # 如果访问此view的请求是来自admin panel的, 重新定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_general'
        else:
            redirect_url = 'club_manager_general'

        
        if new_description == club.description:
            messages.error(request, "The new description cannot duplicate the old description.")
            return redirect(redirect_url, club_id=club_id)

        if not new_description:
            new_description = "This Club hasn't added a Description yet"
            messages.success(request, "Empty content will use the default Description")
        
        club.description = new_description
        club.save()
        messages.success(request, "Description updated successfully.")
        
        return redirect(redirect_url, club_id=club_id)
"""------------------------------------------------------------------------End---------------------------------------------------------------------------"""


"""-------------------------------------------------------------Club Manager Members-------------------------------------------------------------------------"""
"""This section is used to process requests from club manager remove manager"""
"""此部分用于处理来自club manager, admin panel 移除 manager的请求"""
class RemoveManagerView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username):
        club = get_object_or_404(Club, pk=club_id)
        user = get_object_or_404(User, username=username)
        membership = get_object_or_404(Membership, club=club, user=user)

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        # 如果访问此view的请求是来自admin panel的, 重新定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_members'
        else:
            redirect_url = 'club_manager_members'


        # 检查是否是最后一个管理员
        if Membership.objects.filter(club=club, is_manager=True).count() <= 1:
            messages.error(request, "At least one manager is required.")
            return redirect(redirect_url, club_id=club_id)

        # 移除管理员资格
        membership.is_manager = False
        membership.save()
        messages.success(request, f"{user.get_full_name} is no longer a manager.")
        return redirect(redirect_url, club_id=club_id)

"""This section is used to process requests from the club manager and admin panel to add a new manager."""
"""此部分用于处理来自club manager, admin panel 新增 manager的请求"""
class SetManagerView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username):
        club = get_object_or_404(Club, pk=club_id)
        user = get_object_or_404(User, username=username)
        membership = get_object_or_404(Membership, club=club, user=user)

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        # 如果访问此view的请求是来自admin panel的, 重新定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_members'
        else:
            redirect_url = 'club_manager_members'

        # 设置为管理员
        membership.is_manager = True
        membership.save()
        messages.success(request, f"{user.get_full_name} is now a manager.")
        return redirect(redirect_url, club_id=club_id)

"""此部分用来实现club manager - Membership - Add members - 自动搜索框的自动搜索功能"""
class SearchUsersView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        club_id = request.GET.get('club_id')
        
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            account_type=User.ACCOUNT_TYPE_USER
        ).exclude(membership__club_id=club_id)  # 添加排除现有成员的过滤

        results = [{
            'username': user.username,
            'email': user.email,
            'full_name' : user.first_name + user.last_name,
        } for user in users]
        
        return JsonResponse(results, safe=False)
    
"""此部分用来实现club manager 移除 Membership 的功能"""
class RemoveMemberView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username, *args, **kwargs):
        club = get_object_or_404(Club, club_id=club_id)
        user_to_remove = User.objects.filter(username=username).first()

        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        # 如果访问此view的请求是来自admin panel的, 重新定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_members'
        else:
            redirect_url = 'club_manager_members'
        
        # 检查用户是否存在
        if not user_to_remove:
            messages.error(request, "用户不存在")
            return redirect(redirect_url, club_id=club_id)

        membership = Membership.objects.filter(user=user_to_remove, club=club).first()
        # 检查是否有此会员关系
        if not membership:
            messages.error(request, "该用户不属于此社团")
            return redirect(redirect_url, club_id=club_id)
        
        # 检查是否为管理员
        if membership.is_manager:
            messages.error(request, "该用户是管理员，无法直接移除")
            return redirect(redirect_url, club_id=club_id)

        membership.delete()
        messages.success(request, f"{user_to_remove.username} has been removed from the club.")
        return redirect(redirect_url, club_id=club_id)

"""此部分用来实现club manager - 添加member的功能"""
class AddMemberView(LoginRequiredMixin, ClubExistsRequiredMixin, ClubManagerRequiredMixin, View):
    def post(self, request, club_id, username):
        # If the request to access this view came from the admin panel, the redirection url is the admin panel.
        # 如果访问此view的请求是来自admin panel的, 重新定向url就是admin panel
        if request.user.account_type == 'Admin':
            redirect_url = 'admin_panel_club_members'
        else:
            redirect_url = 'club_manager_members'

        try:
            club = Club.objects.get(club_id=club_id)
            user = User.objects.get(username=username)
            
            if Membership.objects.filter(user=user, club=club).exists():
                messages.error(request, f"{user.username} 已是社团成员")
                return redirect(redirect_url, club_id=club_id)
                
            Membership.objects.create(user=user, club=club)
            messages.success(request, f"成功添加成员 {user.get_full_name()}")
            return redirect(redirect_url, club_id=club_id)
            
        except User.DoesNotExist:
            messages.error(request, "用户不存在")
            return redirect(redirect_url, club_id=club_id)
            
        except Exception as e:
            messages.error(request, f"添加失败: {str(e)}")
            return redirect(redirect_url, club_id=club_id)
          
"""----------------------------------------------------------------------End--------------------------------------------------------------"""



    
"""-------------------------------------------------------Club Manager Event 相关-------------------------------------------------------"""
    
class ClubManagerEventGeneral(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, event_id, *args, **kwargs ):
        club = get_object_or_404(Club, club_id=club_id)
        event = get_object_or_404(Event, pk=event_id)
        context = {
            'club': club,
            'event': event,
            'club_id': club_id,
        }
        return render(request, 'club_manager/event/general.html', context)
    
class ClubManagerEventRSVPs(LoginRequiredMixin, ClubManagerRequiredMixin, View):
    def get(self, request, club_id, event_id, *args, **kwargs):
        club = get_object_or_404(Club, pk=club_id)
        event = get_object_or_404(Event, pk=event_id)
        
        # 处理搜索
        search_query = request.GET.get('search', '')
        rsvps = RSVP.objects.filter(event=event).select_related('user')
        
        if search_query:
            rsvps = rsvps.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        context = {
            'club': club,
            'event': event,
            'club_id': club_id,
            'rsvps': rsvps,
            'search_query': search_query,
        }
        return render(request, 'club_manager/event/RSVPs.html', context)
    
"""-------------------------------------------------------Club Manager Event 相关结束-------------------------------------------------------"""




"""-------------------------------------------------------User New Club Requests 相关-------------------------------------------------------"""
"""此方法用来渲染用户申请新Club的form"""
class ApplyNewClubView(LoginRequiredMixin, UserTypeRequiredMixin, View):
    allowed_types = ['User']
    template_name = 'apply_new_club.html'

    def get(self, request):
        form = NewClubRequestForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = NewClubRequestForm(request.POST)
        if form.is_valid():
            club_name = form.cleaned_data['name']
            
            # 检查是否与现有Club重名
            if isSameClubNameExist(club_name):
                messages.error(request, "A club with this name already exists.")
                return render(request, self.template_name, {'form': form})
            
            # 检查是否与待审核的请求重名
            if isSameClubNameExistInRequest(club_name):
                messages.error(request, "A request for a club with this name is already pending.")
                return render(request, self.template_name, {'form': form})
            
            # 创建新的请求
            new_request = form.save(commit=False)
            new_request.creator = request.user
            new_request.save()
            
            admins = User.objects.filter(account_type='Admin')
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="New Club Request",
                    message=f"A new club request '{new_request.name}' has been submitted. Click 'continue' to check the request.",
                    notification_type='general',
                    url=reverse('admin_panel_new_club_requests_detail' , args=[new_request.request_id])
                )
            
            messages.success(request, "Your club creation request has been submitted and is pending approval.")
            return redirect('dashboard_new_club_requests')
        
        # 如果表单无效
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {'form': form})
"""-------------------------------------------------------User New Club Requests 相关结束-------------------------------------------------------"""
